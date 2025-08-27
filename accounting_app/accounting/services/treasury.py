from decimal import Decimal
from datetime import date
from django.db.models import Sum

from accounting.models import Safe, ReceiptVoucher, PaymentVoucher

def get_safe_balance(safe: Safe, to_date: date = None) -> Decimal:
    """
    حساب الرصيد الحالي لخزنة معينة حتى تاريخ محدد (شامل).

    الرصيد = (مجموع مبالغ سندات القبض) - (مجموع مبالغ سندات الصرف)
    """

    receipts_query = ReceiptVoucher.objects.filter(safe=safe)
    payments_query = PaymentVoucher.objects.filter(safe=safe)

    if to_date:
        receipts_query = receipts_query.filter(date__lte=to_date)
        payments_query = payments_query.filter(date__lte=to_date)

    total_receipts = receipts_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
    total_payments = payments_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')

    balance = total_receipts - total_payments
    return balance

def get_safe_movement(safe: Safe, from_date: date, to_date: date) -> dict:
    """
    حساب حركة الخزنة (الإيرادات والمصروفات) خلال فترة محددة.
    """
    receipts_query = ReceiptVoucher.objects.filter(safe=safe, date__range=(from_date, to_date))
    payments_query = PaymentVoucher.objects.filter(safe=safe, date__range=(from_date, to_date))

    total_receipts = receipts_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')
    total_payments = payments_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')

    net_change = total_receipts - total_payments

    return {
        'total_receipts': total_receipts,
        'total_payments': total_payments,
        'net_change': net_change
    }
