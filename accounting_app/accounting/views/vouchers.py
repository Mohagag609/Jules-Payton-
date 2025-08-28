from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import logging

from accounting.models import ReceiptVoucher, PaymentVoucher
from accounting.forms import ReceiptVoucherForm, PaymentVoucherForm

logger = logging.getLogger('accounting')

# --- Receipt Voucher Views ---

@login_required
def receipt_voucher_list_view(request):
    form = ReceiptVoucherForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                receipt = form.save()
                messages.success(request, f'تم إضافة سند القبض بنجاح!')
                
                response = render(request, 'accounting/vouchers/_receipt_row.html', {'receipt': receipt})
                response['HX-Trigger'] = 'receiptAdded'
                return response
            except Exception as e:
                logger.error(f'Error creating receipt voucher: {str(e)}', exc_info=True)
                messages.error(request, f'حدث خطأ: {str(e)}')
                return render(request, 'accounting/vouchers/_receipt_form_container.html', {'form': form}, status=400)
        else:
            # Return form with errors
            return render(request, 'accounting/vouchers/_receipt_form_container.html', {'form': form}, status=400)

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
    if request.method == 'POST':
        if form.is_valid():
            try:
                payment = form.save()
                messages.success(request, f'تم إضافة سند الصرف بنجاح!')
                
                response = render(request, 'accounting/vouchers/_payment_row.html', {'payment': payment})
                response['HX-Trigger'] = 'paymentAdded'
                return response
            except Exception as e:
                logger.error(f'Error creating payment voucher: {str(e)}', exc_info=True)
                messages.error(request, f'حدث خطأ: {str(e)}')
                return render(request, 'accounting/vouchers/_payment_form_container.html', {'form': form}, status=400)
        else:
            # Return form with errors
            return render(request, 'accounting/vouchers/_payment_form_container.html', {'form': form}, status=400)

    payments = PaymentVoucher.objects.select_related('safe', 'supplier', 'project').all()
    context = {
        'payments': payments,
        'form': form,
        'page_title': 'سندات الصرف'
    }
    return render(request, 'accounting/vouchers/payments.html', context)
