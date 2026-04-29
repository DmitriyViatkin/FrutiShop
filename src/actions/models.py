"""
Actions application models for FrutiShop.

Tracks user activities and Celery task metadata. Declaration model manages
file uploads from users. TaskMeta monitors async task execution status, queue
assignments, and execution history for auditing and debugging.
"""
from django.db import models
from user.models import User


class Declaration(models.Model):
    """
    Stores user-uploaded declaration files.

    Declarations are documents uploaded by users for various business purposes.
    Each declaration is linked to a user and timestamped for tracking.

    Files are stored in 'declarations/' subdirectory (configurable in settings.py
    MEDIA_ROOT). On user deletion, all their declarations are removed.
    """
    file = models.FileField(upload_to='declarations/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='declarations'
    )

    def __str__(self):
        return f'Declaration: {self.uploaded_by} at {self.uploaded_at}'


class TaskMeta(models.Model):
    """
    Metadata registry for Celery async tasks.

    Tracks the lifecycle of Celery tasks - from creation through completion.
    Stores task execution status, queue assignment, and results. Supports
    multiple task queues for priority handling. Useful for:
    - Task status polling in rest endpoints
    - Long-running operation tracking (upload processing, etc.)
    - Audit trail of background job execution

    Some tasks can be system-level (user=null) without user context.
    """
    QUEUE_CHOICES = (
        ('queue_1', 'Queue 1'),
        ('queue_2', 'Queue 2'),
        ('audit', 'Audit'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failure', 'Failure'),
    )
    task_id = models.CharField(max_length=255, unique=True)
    task_name = models.CharField(max_length=255)
    queue = models.CharField(max_length=50, choices=QUEUE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    result = models.TextField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )

    def __str__(self):
        return f'TaskMeta: {self.task_id} - {self.status}'
