"""
Treasury Views
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from accounting.models import Safe, Transfer, ReceiptVoucher, PaymentVoucher


@login_required
def treasury_dashboard(request):
    """Treasury dashboard"""
    safes = Safe.objects.all()
    
    # Calculate totals
    total_balance = safes.aggregate(total=Sum('balance'))['total'] or 0
    
    # Recent transfers
    recent_transfers = Transfer.objects.all().order_by('-date')[:10]
    
    return render(request, 'accounting/treasury/dashboard.html', {
        'safes': safes,
        'total_balance': total_balance,
        'recent_transfers': recent_transfers
    })


@login_required
def safe_list(request):
    """List all safes"""
    from .safes import safe_list_view
    return safe_list_view(request)


@login_required
def transfer_list(request):
    """List transfers"""
    from .transfers import transfer_list
    return transfer_list(request)