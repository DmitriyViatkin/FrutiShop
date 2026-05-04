from django.urls import path
from . import views

urlpatterns = [
    path('', views.trading_dashboard, name='trading_dashboard'),
    path('stocks/', views.stock_list, name='stock_list'),
    path('toggle-tasks/<str:action>/', views.toggle_supply_tasks,
         name='toggle_tasks'),
    path('last-dates/', views.last_task_dates, name='last_task_dates'),

    # ── Ручний запуск тасок з фронтенду ──────────────────────────────
    path('stock/buy/', views.buy_fruit, name='buy_fruit'),
    path('stock/sell/', views.sell_fruit, name='sell_fruit'),
    path('audit/inventory/', views.start_audit_inventory,
         name='run_inventory_audit'),
    path('audit/bank/', views.start_audit_bank, name='run_bank_audit'),

    # ----пополнение баланса------
    path('bank/deposit/', views.deposit, name='deposit'),
    path('bank/withdraw/', views.withdraw, name='withdraw'),


]

