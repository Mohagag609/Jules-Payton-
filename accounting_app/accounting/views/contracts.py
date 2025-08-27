from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.urls import reverse

from accounting.models import Contract, Safe, ReceiptVoucher
from accounting.forms import ContractForm
from accounting.services.contracts import generate_installments_for_contract

@login_required
def contract_list_view(request):
    contracts = Contract.objects.select_related('customer', 'unit').all()
    context = {
        'contracts': contracts,
        'page_title': 'العقود'
    }
    return render(request, 'accounting/contracts/list.html', context)

@login_required
def contract_detail_view(request, pk):
    contract = get_object_or_404(
        Contract.objects.select_related('customer', 'unit', 'partners_group'),
        pk=pk
    )
    installments = contract.installments.all()
    context = {
        'contract': contract,
        'installments': installments,
        'page_title': f'تفاصيل العقد {contract.code}'
    }
    return render(request, 'accounting/contracts/detail.html', context)

@login_required
@transaction.atomic
def contract_create_view(request):
    """
    A simple wizard-like view for creating a contract.
    - Step 1 (GET/POST): Fill out the contract form.
    - Step 2 (POST from step 1): Preview installments and confirm.
    """
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            # Don't save yet. Create an instance and generate installments.
            contract_instance = form.save(commit=False)

            # This is the final confirmation step
            if 'confirm_creation' in request.POST:
                contract_instance.save()
                generate_installments_for_contract(contract_instance)
                # Also create the down payment voucher if amount > 0
                if contract_instance.down_payment > 0:
                    safe_id = request.POST.get('down_payment_safe')
                    safe = get_object_or_404(Safe, pk=safe_id) if safe_id else Safe.objects.first()
                    if safe:
                        ReceiptVoucher.objects.create(
                            date=contract_instance.start_date,
                            amount=contract_instance.down_payment,
                            safe=safe,
                            description=f"الدفعة المقدمة للعقد {contract_instance.code}",
                            customer=contract_instance.customer,
                            contract=contract_instance
                        )

                return redirect(reverse('accounting:contracts:detail', kwargs={'pk': contract_instance.pk}))

            # This is the preview step
            context = {
                'form_data': request.POST,
                'contract': contract_instance,
                'safes': Safe.objects.all(),
                'page_title': 'مراجعة و تأكيد العقد'
            }
            return render(request, 'accounting/contracts/create_wizard_preview.html', context)
    else:
        form = ContractForm()

    context = {
        'form': form,
        'page_title': 'إنشاء عقد جديد - الخطوة ١'
    }
    return render(request, 'accounting/contracts/create_wizard_form.html', context)
