"""
Communication application models for FrutiShop.

Manages user messaging and content delivery. Message model stores user-to-user
or system-to-user communications. Joke model stores humorous content for
distribution or display.
"""
from django.db import models
from user.models import User


class Message(models.Model):
    """
    Stores messages between users or from system to users.

    Represents a single message/notification. Sender is stored as text field
    to support both user messages and system notifications. User field is
    optional to allow system-generated messages without explicit user context.
    Can be extended to support read status, message threads, or encryption.
    """

    sender = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages'
    )

    def __str__(self):
        return f'Message from {self.sender} at {self.timestamp}'


class Joke(models.Model):
    """
    Stores joke content for distribution or display.

    Simple model to store humorous content. Could be used for:
    - Daily joke notifications/API endpoints
    - User engagement/entertainment features
    - Testing message distribution systems
    """
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Joke at {self.timestamp}'
