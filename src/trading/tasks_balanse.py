import time
from django.db.models import F
from asyncio import timeout
from django.http import HttpResponse
from .models import Account
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from asgiref.sync import async_to_sync
from celery import shared_task, current_app
from channels.layers import get_channel_layer
from django.core.cache import cache
from .tasks import send_ws

@shared_task( queue="queue_1")
def deposit_task(amount:str):

    with transaction.atomic():
        Account.objects.filter(pk=2).update(balance=F('balance') + Decimal(amount))
        account = Account.objects.select_for_update().get(pk=2)

    now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    msg=( f'{now} — 💰 Депозит {amount} USD успішно зараховано. Поточний баланс: {Account.objects.get(pk=2).balance} USD')
    send_ws(msg, balance=str(account.balance))

@shared_task( queue="queue_1")
def withdraw_task(amount: str):
    with transaction.atomic():
        account = Account.objects.select_for_update().get(pk=2)
        amount_decimal = Decimal(amount)
        if account.balance < amount_decimal:
            msg = f'❌Недостатньо коштів. Баланс: {account.balance} USD'

            send_ws(msg, balance=str(account.balance), error=True)
            return
        account.balance -= amount_decimal
        account.save()
    msg = f'Зняття {amount} USD виконано. Баланс: {account.balance} USD'
    send_ws(msg, balance=str(account.balance))