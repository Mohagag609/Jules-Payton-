from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum, Q, F

from accounting.models import (
    Safe, ReceiptVoucher, PaymentVoucher, Installment, Customer, Partner, Project, Supplier
)
from .treasury import get_safe_balance

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

def get_installments_report_data(customer: Customer = None, status: str = None):
    """
    Prepares data for the Installments Report.
    - Filters by customer and/or status.
    - Calculates totals for amount, paid_amount, and remaining.
    """
    installments = Installment.objects.select_related('contract__customer').all()

    if customer:
        installments = installments.filter(contract__customer=customer)
    if status and status in ['PENDING', 'PAID', 'LATE']:
        # Ensure statuses are up-to-date before filtering
        for inst in installments.filter(status__in=['PENDING', 'LATE']):
            inst.update_status()
        installments = installments.filter(status=status)

    # Annotate remaining amount
    installments = installments.annotate(
        remaining_amount=F('amount') - F('paid_amount')
    )

    totals = installments.aggregate(
        total_amount=Sum('amount'),
        total_paid=Sum('paid_amount'),
        total_remaining=Sum('remaining_amount')
    )

    return {
        'installments': installments,
        'totals': totals
    }

def get_partner_balances_report_data():
    """
    Prepares data for the Partner Balances Report.
    Fetches all partner wallets and their current balances.
    """
    partner_wallets = Safe.objects.filter(is_partner_wallet=True).select_related('partner')
    report_data = []
    for wallet in partner_wallets:
        report_data.append({
            'partner_name': wallet.partner.name,
            'wallet_name': wallet.name,
            'balance': get_safe_balance(wallet)
        })
    return report_data

def get_expenses_report_data(from_date: date, to_date: date, project: Project = None, supplier: Supplier = None):
    """
    Prepares data for the Expenses Report.
    Filters payment vouchers by date range and optionally by project or supplier.
    """
    expenses = PaymentVoucher.objects.filter(date__range=(from_date, to_date)) \
                                     .select_related('project', 'supplier', 'safe')

    if project:
        expenses = expenses.filter(project=project)
    if supplier:
        expenses = expenses.filter(supplier=supplier)

    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')

    return {
        'expenses': expenses.order_by('-date'),
        'total_expenses': total_expenses
    }
