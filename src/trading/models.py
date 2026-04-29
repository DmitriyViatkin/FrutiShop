"""
Trading application models for FrutiShop.

Handles inventory management, account balance tracking, and transaction records
for the fruit marketplace system. Work in conjunction with Celery tasks for
async processing of buy/sell operations.
"""
from django.db import models


class Inventory(models.Model):
    """
    Tracks available stock levels for each fruit type in the marketplace.

    Each fruit has a unique inventory record. Quantity represents the current
    available units for sale. Use this model to validate stock availability
    before processing purchase transactions.
    """
    FRUIT_CHOICES = (
        ('apple', 'Apple'),
        ('banana', 'Banana'),
        ('pineapple', 'Pineapple'),
        ('peach', 'Peach'),
    )

    fruit = models.CharField(max_length=50, choices=FRUIT_CHOICES, unique=True)
    quantity = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.fruit} - {self.quantity} units'


class Account(models.Model):
    """
    Stores the marketplace account balance.

    Represents total funds available for purchasing fruits. Updated when
    transactions succeed. Note: Currently generic - can be extended to
    support multiple user accounts by adding ForeignKey to User.
    """

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Balance: ${self.balance}'


class OrderTransaction(models.Model):
    """
    Records all buy/sell transactions (successful and failed).

    Each transaction represents an attempt to buy or sell fruit. Success status
    indicates whether the transaction was processed. Failed transactions are
    logged with a reason (insufficient funds, not enough goods) for auditing
    and debugging purposes.

    Indexed on created_at for efficient historical queries.
    """
    TRANSACTION_TYPES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )
    FRUIT_CHOICES = (
        ('apple', 'Apple'),
        ('banana', 'Banana'),
        ('pineapple', 'Pineapple'),
        ('peach', 'Peach'),
    )
    REASON_CHOICES = (
        ('not_enough_goods', 'Not enough goods'),
        ('insufficient_funds', 'Insufficient funds'),
    )

    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    fruit = models.CharField(max_length=50, choices=FRUIT_CHOICES)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    success = models.BooleanField(default=False)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        indexes = [models.Index(fields=['created_at'])]

    def __str__(self):
        return f'{self.transaction_type} {self.fruit} {self.quantity} units at ${self.price}'