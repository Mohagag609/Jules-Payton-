from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import date, timedelta

from accounting.models import ReceiptVoucher, PaymentVoucher, Installment

@login_required
def dashboard_view(request):
    """
    View for the main dashboard, displaying key performance indicators (KPIs)
    and recent activities.
    """

    # --- KPI Calculations ---

    # Total Receipts and Payments
    total_receipts = ReceiptVoucher.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
    total_payments = PaymentVoucher.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
    net_balance = total_receipts - total_payments

    # Late Installments Count
    today = date.today()
    late_installments_count = Installment.objects.filter(
        status=Installment.InstallmentStatus.PENDING,
        due_date__lt=today
    ).count()

    # --- Data for Tables ---

    # Recent Vouchers (mixing receipts and payments)
    # This is a bit complex to do efficiently with standard ORM.
    # For simplicity, we'll fetch last 5 of each and interleave them in python.
    # A more robust solution might use a union or a custom view/model.
    last_receipts = ReceiptVoucher.objects.select_related('safe').order_by('-created_at')[:5]
    last_payments = PaymentVoucher.objects.select_related('safe').order_by('-created_at')[:5]

    # --- Alerts ---

    # Installments due soon
    next_7_days = today + timedelta(days=7)
    due_soon_installments = Installment.objects.filter(
        status=Installment.InstallmentStatus.PENDING,
        due_date__range=[today, next_7_days]
    ).select_related('contract__customer')

    # Late installments
    late_installments = Installment.objects.filter(
        status=Installment.InstallmentStatus.LATE
    ).select_related('contract__customer')

    # (Low stock and budget alerts will be implemented with their respective modules)

    context = {
        'total_receipts': total_receipts,
        'total_payments': total_payments,
        'net_balance': net_balance,
        'late_installments_count': late_installments_count,
        'last_receipts': last_receipts,
        'last_payments': last_payments,
        'due_soon_installments': due_soon_installments,
        'late_installments': late_installments,
        'page_title': 'لوحة التحكم الرئيسية' # For the navbar or header
    }

    return render(request, 'accounting/dashboard.html', context)
