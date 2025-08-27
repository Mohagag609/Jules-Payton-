import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from accounting.models import Installment
from accounting.forms import InstallmentPaymentForm
from accounting.services.installments import pay_installment

@login_required
def installment_list_view(request):
    """
    Renders the list of all installments with filters.
    """
    installments = Installment.objects.select_related('contract__customer').all()

    # Filtering logic
    status_filter = request.GET.get('status')
    if status_filter and status_filter in ['PENDING', 'PAID', 'LATE']:
        installments = installments.filter(status=status_filter)

    # Update status for PENDING/LATE installments on each load
    # This is not super efficient for large datasets, a cron job would be better.
    for inst in installments:
        if inst.status != 'PAID':
            inst.update_status()

    context = {
        'installments': installments,
        'page_title': 'الأقساط'
    }
    return render(request, 'accounting/installments/list.html', context)

@login_required
def installment_pay_view(request, pk):
    """
    Handles paying an installment via a modal form.
    """
    installment = get_object_or_404(Installment, pk=pk)
    if request.method == 'POST':
        form = InstallmentPaymentForm(request.POST, installment=installment)
        if form.is_valid():
            pay_installment(
                installment=installment,
                amount=form.cleaned_data['amount'],
                safe=form.cleaned_data['safe'],
                payment_date=form.cleaned_data['date']
            )
            # Return the updated row for HTMX and trigger modal close
            response = render(request, 'accounting/installments/_row.html', {'installment': installment})
            response['HX-Trigger'] = json.dumps({"closeModal": None, "showToast": {"message": "تم تسجيل الدفعة بنجاح!", "type": "success"}})
            return response
    else:
        form = InstallmentPaymentForm(installment=installment)

    context = {
        'form': form,
        'installment': installment
    }
    return render(request, 'accounting/installments/_pay_dialog.html', context)
