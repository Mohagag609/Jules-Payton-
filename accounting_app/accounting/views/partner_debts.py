"""
Partner Debts Views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from accounting.models import PartnerDebt


@login_required
def debt_list(request):
    """List all partner debts"""
    debts = PartnerDebt.objects.all().select_related(
        'unit', 'paying_partner', 'owed_partner'
    ).order_by('-due_date')
    
    return render(request, 'accounting/partner_debts/list.html', {
        'debts': debts
    })


@login_required
def debt_pay(request, pk):
    """Pay a partner debt"""
    debt = get_object_or_404(PartnerDebt, pk=pk)
    
    if request.method == 'POST':
        if debt.status == 'paid':
            messages.warning(request, 'هذا الدين مدفوع بالفعل')
        else:
            debt.status = 'paid'
            debt.payment_date = timezone.now().date()
            debt.save()
            messages.success(request, 'تم تسجيل دفع الدين بنجاح')
        
        return redirect('partner_debts:debt_list')
    
    return render(request, 'accounting/partner_debts/pay.html', {
        'debt': debt
    })