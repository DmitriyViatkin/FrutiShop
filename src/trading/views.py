from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from trading import models
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
