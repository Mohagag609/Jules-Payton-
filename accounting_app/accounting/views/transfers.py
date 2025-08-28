"""
Transfers Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounting.models import Transfer
from accounting.forms import TransferForm


@login_required
def transfer_list(request):
    """List all transfers"""
    transfers = Transfer.objects.all().select_related('from_safe', 'to_safe')
    return render(request, 'accounting/transfers/list.html', {
        'transfers': transfers
    })


@login_required
def transfer_create(request):
    """Create a new transfer"""
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            transfer = form.save()
            messages.success(request, f'تم التحويل بنجاح: {transfer.amount} ج.م')
            return redirect('transfers:transfer_list')
    else:
        form = TransferForm()
    
    return render(request, 'accounting/transfers/form.html', {
        'form': form,
        'title': 'تحويل جديد بين الخزن'
    })


@login_required
def transfer_detail(request, pk):
    """Transfer detail view"""
    transfer = get_object_or_404(Transfer, pk=pk)
    return render(request, 'accounting/transfers/detail.html', {
        'transfer': transfer
    })