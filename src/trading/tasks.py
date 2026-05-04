import random
from django.utils import timezone
import logging
from decimal import Decimal
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import  transaction
from .models import OrderTransaction, Inventory, Account
logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()

FRUIT_CONFIG = {
    #          buy_range   sell_range   buy_price  sell_price
    'apple':     ((1, 10),  (1, 10),      4,     5, ),
    'banana':    ((10, 20), (1, 30),     1 ,    2, ),
    'pineapple': ((1, 10),  (1, 10),      3 ,   4,),
    'peach':     ((5, 15),  (1, 20),     2 ,    3),
}

def send_ws(message: str, balance=None,error=False):
    payload = {
        'type': 'fruit.log',
        'message': str(message),
        'error': error,  # ← повертаємо error замість level
    }
    if balance is not None:
        payload['balance'] = str(balance)
    async_to_sync(channel_layer.group_send)('fruit_trading', payload)

def _buy(fruit:str, manual_qty = None):
    cfg = FRUIT_CONFIG[fruit]
    qty = int(manual_qty) if manual_qty is not None else random.randint(*cfg[0])

    buy_price = Decimal(str(cfg[2]))
    cost = buy_price * qty

    logger.info(f"BUY attempt: {fruit.upper()} x{qty} @ ${buy_price} = ${cost}")
    with transaction.atomic():
        account = Account.objects.select_for_update().get(pk=2)
        now = timezone.now().strftime("%H:%M")
        if account.balance < cost:
            msg = (f" {now} - BUY {fruit.upper()} x{qty} "
                   f"— недостатньо коштів (потрібно ${cost}, є ${account.balance})")
            logger.warning(msg)
            OrderTransaction.objects.create(
                transaction_type='BUY', fruit=fruit, quantity=qty,
                price=buy_price, success= False, reason='insufficient_funds'
            )
            send_ws(msg, balance=account.balance, error=True)
            return msg

        account.balance -= cost
        account.save()
        inventory, _ = Inventory.objects.get_or_create(fruit=fruit, defaults={'quantity': 0})
        inventory.quantity += qty
        inventory.save()

    msg = f"{now} - BUY {fruit.upper()} x{qty} @ ${buy_price} = ${cost} | баланс: ${account.balance}"
    logger.info(msg)
    OrderTransaction.objects.create(
        transaction_type='BUY', fruit=fruit, quantity=qty,
        price=buy_price, success=True
    )
    send_ws(msg, balance=account.balance)
    return msg

def _sell(fruit:str, manual_qty = None):
    cfg = FRUIT_CONFIG[fruit]
    qty = int(manual_qty) if manual_qty is not None else random.randint(*cfg[1])

    sell_price= Decimal(str(cfg[3]))
    revenue  = sell_price * qty


    logger.info(f"SELL attempt: {fruit.upper()} x{qty} @ ${sell_price} = ${revenue}")
    with transaction.atomic():
        try:

            inventory = Inventory.objects.select_for_update().get(fruit=fruit)

        except Inventory.DoesNotExist:
            inventory = None

        if inventory.quantity < qty:
            msg = (f" SELL {fruit.upper()} x{qty} "
                   f"— недостатньо товара (потрібно {qty}, есть {inventory.quantity})")
            logger.warning(msg)
            OrderTransaction.objects.create(
                transaction_type='SELL', fruit=fruit, quantity=qty,
                price=sell_price, success=False, reason='not_enough_goods'
            )
            send_ws(msg, error=True)
            return msg
        inventory.quantity -= qty
        inventory.save()
        account = Account.objects.select_for_update().get(pk=2)
        account.balance += revenue
        account.save()

    msg = f"SELL {fruit.upper()} x{qty} @ ${sell_price} = ${revenue} | баланс: ${account.balance}"
    logger.info(msg)
    OrderTransaction.objects.create(
        transaction_type='SELL', fruit=fruit, quantity=qty,
        price=sell_price, success=True
    )
    send_ws(msg, balance=account.balance)
    return msg


# ── Buy tasks ──────────────────────────────────────────
@shared_task(queue='queue_1')
def buy_apple(qty=None):     return _buy('apple', manual_qty=qty)

@shared_task(queue='queue_1')
def buy_banana(qty=None):    return _buy('banana', manual_qty=qty)

@shared_task(queue='queue_1')
def buy_pineapple(qty=None): return _buy('pineapple', manual_qty=qty)

@shared_task(queue='queue_1')
def buy_peach(qty=None):     return _buy('peach', manual_qty=qty)


# ── Sell tasks ─────────────────────────────────────────
@shared_task(queue='queue_1')
def sell_apple(qty=None):     return _sell('apple', manual_qty=qty)

@shared_task(queue='queue_1')
def sell_banana(qty=None):    return _sell('banana', manual_qty=qty)

@shared_task(queue='queue_1')
def sell_pineapple(qty=None): return _sell('pineapple', manual_qty=qty)

@shared_task(queue='queue_1')
def sell_peach(qty=None):     return _sell('peach', manual_qty=qty)