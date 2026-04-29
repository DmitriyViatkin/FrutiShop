"""
User application models for FrutiShop.

Custom User model extending Django's AbstractUser. This is the primary identity
model used throughout the entire application. Always import from src.user.models
instead of Django's default User model.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model for FrutiShop.

    Extends Django's AbstractUser to maintain compatibility with all built-in
    authentication features, while allowing for future custom fields and methods.

    Inherits fields: username, email, password, first_name, last_name, is_active,
    is_staff, is_superuser, last_login, date_joined.

    Used by:
    - Declaration (actions app) - tracks uploaded documents
    - TaskMeta (actions app) - tracks Celery task ownership
    - Message (communication app) - message recipients
    - All future models requiring user identification
    """

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'