from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum

from accounting.models import Safe, ReceiptVoucher, PaymentVoucher

def get_treasury_report_data(from_date: date, to_date: date, safe: Safe = None):
    """
    Prepares data for the Treasury Report.
    - Opening Balance
    - List of all transactions in the period
    - Closing Balance
    """

    # Determine the queryset for safes
    safes = Safe.objects.all()
    if safe:
        safes = safes.filter(pk=safe.pk)

    report_data = []

    for s in safes:
        # Calculate opening balance (balance at the start of from_date)
        opening_balance_date = from_date - timedelta(days=1)
        receipts_before = ReceiptVoucher.objects.filter(safe=s, date__lte=opening_balance_date).aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
        payments_before = PaymentVoucher.objects.filter(safe=s, date__lte=opening_balance_date).aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
        opening_balance = receipts_before - payments_before

        # Get transactions within the period
        receipts_in_period = list(ReceiptVoucher.objects.filter(safe=s, date__range=(from_date, to_date)).order_by('date'))
        payments_in_period = list(PaymentVoucher.objects.filter(safe=s, date__range=(from_date, to_date)).order_by('date'))

        # Combine and sort transactions by date
        transactions = sorted(
            receipts_in_period + payments_in_period,
            key=lambda t: t.date
        )

        # Calculate closing balance
        total_receipts_in_period = sum(t.amount for t in receipts_in_period)
        total_payments_in_period = sum(t.amount for t in payments_in_period)
        closing_balance = opening_balance + total_receipts_in_period - total_payments_in_period

        report_data.append({
            'safe': s,
            'opening_balance': opening_balance,
            'transactions': transactions,
            'total_receipts': total_receipts_in_period,
            'total_payments': total_payments_in_period,
            'closing_balance': closing_balance,
        })

    return report_data
