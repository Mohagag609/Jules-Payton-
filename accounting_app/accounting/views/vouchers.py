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
            # This is a simple create, so we just return the new row
            return render(request, 'accounting/vouchers/_receipt_row.html', {'receipt': receipt})
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
            return render(request, 'accounting/vouchers/_payment_row.html', {'payment': payment})
    else:
        form = PaymentVoucherForm()

    return render(request, 'accounting/vouchers/_payment_form.html', {'form': form})
