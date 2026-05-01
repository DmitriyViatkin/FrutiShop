from django.urls import path
from . import views

urlpatterns = [
    path('', views.trading_dashboard, name='trading_dashboard'),
    path('stocks/', views.stock_list, name='stock_list'),
    path('toggle-tasks/<str:action>/', views.toggle_supply_tasks, name='toggle_tasks'),
    path('last-dates/', views.last_task_dates, name='last_task_dates'),

    # ── Ручний запуск тасок з фронтенду ──────────────────────────────
    path('stock/buy/', views.buy_fruit, name='buy_fruit'),
    path('stock/sell/', views.sell_fruit, name='sell_fruit'),

]