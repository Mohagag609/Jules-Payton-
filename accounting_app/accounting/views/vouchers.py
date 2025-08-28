from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounting.models import ReceiptVoucher, PaymentVoucher
from accounting.forms import ReceiptVoucherForm, PaymentVoucherForm

# --- Receipt Voucher Views ---

@login_required
def receipt_voucher_list_view(request):
    form = ReceiptVoucherForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        receipt = form.save()
        messages.success(request, f'تم إضافة سند القبض رقم {receipt.voucher_number} بنجاح!')
        
        response = render(request, 'accounting/vouchers/_receipt_row.html', {'receipt': receipt})
        response['HX-Trigger'] = 'receiptAdded'
        return response

    receipts = ReceiptVoucher.objects.select_related('safe', 'customer', 'partner').all()
    context = {
        'receipts': receipts,
        'form': form,
        'page_title': 'سندات القبض'
    }
    return render(request, 'accounting/vouchers/receipts.html', context)

# --- Payment Voucher Views ---

@login_required
def payment_voucher_list_view(request):
    form = PaymentVoucherForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        payment = form.save()
        messages.success(request, f'تم إضافة سند الصرف رقم {payment.voucher_number} بنجاح!')
        
        response = render(request, 'accounting/vouchers/_payment_row.html', {'payment': payment})
        response['HX-Trigger'] = 'paymentAdded'
        return response

    payments = PaymentVoucher.objects.select_related('safe', 'supplier', 'project').all()
    context = {
        'payments': payments,
        'form': form,
        'page_title': 'سندات الصرف'
    }
    return render(request, 'accounting/vouchers/payments.html', context)
