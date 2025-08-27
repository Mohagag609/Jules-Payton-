import json
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from accounting.models import ReceiptVoucher, PaymentVoucher
from accounting.forms import ReceiptVoucherForm, PaymentVoucherForm

# --- Receipt Voucher Views ---

@login_required
def receipt_voucher_list_view(request):
    receipts = ReceiptVoucher.objects.select_related('safe', 'customer', 'partner').all()
    context = {
        'receipts': receipts,
        'page_title': 'سندات القبض'
    }
    return render(request, 'accounting/vouchers/receipts.html', context)

@login_required
def receipt_voucher_create_view(request):
    if request.method == 'POST':
        form = ReceiptVoucherForm(request.POST)
        if form.is_valid():
            receipt = form.save()
            response = render(request, 'accounting/vouchers/_receipt_row.html', {'receipt': receipt})
            response['HX-Trigger'] = json.dumps({"closeModal": None, "showToast": {"message": "تم إنشاء سند القبض بنجاح!", "type": "success"}})
            return response
    else:
        form = ReceiptVoucherForm()

    return render(request, 'accounting/vouchers/_receipt_form.html', {'form': form})


# --- Payment Voucher Views ---

@login_required
def payment_voucher_list_view(request):
    payments = PaymentVoucher.objects.select_related('safe', 'supplier', 'project').all()
    context = {
        'payments': payments,
        'page_title': 'سندات الصرف'
    }
    return render(request, 'accounting/vouchers/payments.html', context)

@login_required
def payment_voucher_create_view(request):
    if request.method == 'POST':
        form = PaymentVoucherForm(request.POST)
        if form.is_valid():
            payment = form.save()
            response = render(request, 'accounting/vouchers/_payment_row.html', {'payment': payment})
            response['HX-Trigger'] = json.dumps({"closeModal": None, "showToast": {"message": "تم إنشاء سند الصرف بنجاح!", "type": "success"}})
            return response
    else:
        form = PaymentVoucherForm()

    return render(request, 'accounting/vouchers/_payment_form.html', {'form': form})
