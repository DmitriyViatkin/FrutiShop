from gc import enable
from django.utils import timezone
from celery import current_app
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django_celery_beat.models import PeriodicTask,PeriodicTasks
from . import tasks as trading_tasks
from django.views.decorators.http import require_POST
from .models import OrderTransaction,Account,Inventory


#@login_required
def trading_dashboard(request):
    """
    Renders the main trading interface.

    Displays current inventory levels, account balance, and recent transactions.
    Provides forms for buying/selling fruits. Data is fetched from the database
    and passed to the template for rendering. User must be authenticated to
    access this view.
    """
    inventory = Inventory.objects.all()
    account = Account.objects.first()  # Assuming a single account for simplicity
    transactions = OrderTransaction.objects.order_by('-created_at')[:50]  # Last 10 transactions

    context = {
        'inventory': inventory,
        'account': account,
        'transactions': transactions,
    }
    return render(request, 'trading/index.html', context)

def stock_list(request):
    """
    Renders a list of available stocks (fruits) for trading.

    Displays current inventory levels and prices. Provides options to buy/sell
    each fruit. Data is fetched from the database and passed to the template
    for rendering.
    """
    inventory = Inventory.objects.all()
    context = {
        'inventory': inventory,
    }
    return render(request, 'includes/table_fruit.html', context)

# Керування періодичними завданнями
def toggle_supply_tasks(request, action):
    """
    Toggles the state of periodic supply tasks.

    Enables or disables the periodic tasks responsible for supplying fruits.
    This view can be accessed by an admin user to control the flow of supplies.
    """
    enabled = (action == "start")
    PeriodicTask.objects.filter(name__icontains='Buy').update(enabled=enabled)
    PeriodicTask.objects.filter(name__icontains='Sell').update(enabled=enabled)
    PeriodicTasks.update_changed()
    status_msg = "Запущено" if enabled else "Зупинено"
    from django.utils import timezone
    now = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    return  HttpResponse(
        f'<div class="log-entry log-success">{now} - Система: Торгівлю {status_msg}</div>')

def last_task_dates(request):
    """
    Returns the last execution dates of buy/sell tasks.

    Fetches the last run times of all buy and sell periodic tasks and returns
    them as a JSON response. This can be used for monitoring task activity.
    """
    tasks = PeriodicTask.objects.filter(name__iregex='Buy|sell').values('name', 'last_run_at')
    lines = ''.join(
        f'{t["name"]}: {t["last_run_at"].strftime("%H:%M:%S") if t["last_run_at"] else "—"}<br>'
        for t in tasks
    )
    return HttpResponse(lines)


@require_POST
def buy_fruit(request):
    fruit = request.POST.get('fruit', '').lower().strip()
     
    quantity = request.POST.get('quantity')

    now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    valid_fruits = {'apple', 'banana', 'pineapple', 'peach'}

    if fruit not in valid_fruits:
        return HttpResponse(
            f'<div class="log-entry log-error">{now} — ❌ Помилка: {fruit}</div>')


    qty_val = int(quantity) if quantity and quantity.isdigit() else None

    current_app.send_task(
        f'trading.tasks.buy_{fruit}',
        args=[qty_val],  # Передаємо аргумент списком
        queue='queue_1'
    )

    return HttpResponse(
        f'<div class="log-entry log-success">{now} — ⏳ Запит на покупку {fruit} x{qty_val or "авто"} надіслано</div>')




@require_POST
def sell_fruit(request):
    """
    Triggers a sell task for the given fruit via HTMX.
    Returns an HTML log entry that gets prepended to #log-list.

    POST params:
        fruit — one of apple / banana / pineapple / peach
    """
    quantity = request.POST.get('quantity')
    qty_val = int(quantity) if quantity and quantity.isdigit() else None
    fruit = request.POST.get('fruit', '').lower().strip()
    now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    valid_fruits = {'apple', 'banana', 'pineapple', 'peach'}

    if fruit not in valid_fruits:
        return HttpResponse(
            f'<div class="log-entry log-error">'
            f'{now} — ❌ Невідомий фрукт: «{fruit}»'
            f'</div>'
        )
    current_app.send_task(f'trading.tasks.sell_{fruit}',
                            args=[qty_val] ,
                          queue='queue_1')
    return HttpResponse(
        f'<div class="log-entry log-success">'
        f'{now} — ⏳ Завдання SELL {fruit.upper()} поставлено у чергу'
        f'</div>'
    )
