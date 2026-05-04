from django.urls import path
from .views import login_view, check_user, logout_view

urlpatterns = [
    path('login/', login_view, name='hx_login'),
    path('check-user/', check_user, name='hx_check_user'),
    path('logout/', logout_view, name='hx_logout'),
]