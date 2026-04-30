from django.urls import path
from . import views

urlpatterns = [
    path('', views.trading_dashboard, name='trading_dashboard'),
]