from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import json

from accounting.models import ReceiptVoucher, PaymentVoucher
from accounting.forms import ReceiptVoucherForm, PaymentVoucherForm

# --- Receipt Voucher Views ---

@login_required
def receipt_voucher_list_view(request):
    form = ReceiptVoucherForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            receipt = form.save()
            # Return the row HTML with a success trigger
            html = render(request, 'accounting/vouchers/_receipt_row.html', {'receipt': receipt}).content.decode()
            
            return HttpResponse(
                html,
                headers={
                    'HX-Trigger': json.dumps({
                        'showMessage': {
                            'message': 'تم إضافة سند القبض بنجاح!',
                            'type': 'success'
                        },
                        'closeModal': True
                    })
                }
            )
        else:
            # Return form with errors
            return render(request, 'accounting/vouchers/_receipt_form_container.html', {'form': form})

    receipts = ReceiptVoucher.objects.select_related('safe', 'customer', 'partner').order_by('-date', '-id')
    
    # Calculate statistics
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)
    
    today_total = ReceiptVoucher.objects.filter(
        date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    month_total = ReceiptVoucher.objects.filter(
        date__gte=start_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    year_total = ReceiptVoucher.objects.filter(
        date__gte=start_of_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'receipts': receipts,
        'form': form,
        'page_title': 'سندات القبض',
        'today_total': today_total,
        'month_total': month_total,
        'year_total': year_total,
    }
    return render(request, 'accounting/vouchers/modern_receipts.html', context)

# --- Payment Voucher Views ---

@login_required
def payment_voucher_list_view(request):
    form = PaymentVoucherForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            payment = form.save()
            # Return the row HTML with a success trigger
            html = render(request, 'accounting/vouchers/_payment_row.html', {'payment': payment}).content.decode()
            
            return HttpResponse(
                html,
                headers={
                    'HX-Trigger': json.dumps({
                        'showMessage': {
                            'message': 'تم إضافة سند الصرف بنجاح!',
                            'type': 'success'
                        },
                        'closeModal': True
                    })
                }
            )
        else:
            # Return form with errors
            return render(request, 'accounting/vouchers/_payment_form_container.html', {'form': form})

    payments = PaymentVoucher.objects.select_related('safe', 'supplier', 'project').all()
    context = {
        'payments': payments,
        'form': form,
        'page_title': 'سندات الصرف'
    }
    return render(request, 'accounting/vouchers/payments.html', context)
