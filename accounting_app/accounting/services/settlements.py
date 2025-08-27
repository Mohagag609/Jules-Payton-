from decimal import Decimal
from datetime import date
from django.db import transaction
from django.db.models import Sum

from accounting.models import PartnersGroup, PaymentVoucher, Settlement, Partner, Safe

def calculate_partner_settlement(
    partners_group: PartnersGroup,
    from_date: date,
    to_date: date,
    project_id: int = None
) -> Settlement:
    """
    Calculates the settlement for a group of partners over a given period.
    This version uses explicit loops to be robust, though it's less efficient.
    """

    members = partners_group.members.select_related('partner').all()
    if not members:
        raise ValueError("Cannot calculate settlement for a group with no members.")

    # Get all payments related to the partners in the group for the period
    all_member_partners = [m.partner for m in members]
    all_payments_in_period = PaymentVoucher.objects.filter(
        date__range=(from_date, to_date),
        safe__partner__in=all_member_partners
    )
    if project_id:
        all_payments_in_period = all_payments_in_period.filter(project_id=project_id)

    total_group_expenses = all_payments_in_period.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')

    partner_details = []
    for member in members:
        # For each member, get their specific payments
        member_payments = all_payments_in_period.filter(safe__partner=member.partner)
        paid_amount = member_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.0')

        should_have_paid = (total_group_expenses * member.percent) / Decimal('100.0')
        net_balance = paid_amount - should_have_paid

        partner_details.append({
            'partner_id': member.partner.id,
            'partner_name': member.partner.name,
            'share_percent': float(member.percent),
            'paid_amount': float(paid_amount),
            'should_have_paid': float(should_have_paid),
            'net_balance': float(net_balance)
        })

    # --- Transfer calculation logic ---
    creditors = sorted([p for p in partner_details if p['net_balance'] > 0], key=lambda x: x['net_balance'], reverse=True)
    debtors = sorted([p for p in partner_details if p['net_balance'] < 0], key=lambda x: x['net_balance'])
    transfers = []
    for debtor in debtors:
        amount_to_pay = abs(Decimal(str(debtor['net_balance'])))
        for creditor in creditors:
            if creditor['net_balance'] > 0:
                transfer_amount = min(amount_to_pay, Decimal(str(creditor['net_balance'])))
                if transfer_amount > 0:
                    transfers.append({
                        'from': debtor['partner_name'],
                        'to': creditor['partner_name'],
                        'amount': float(transfer_amount)
                    })
                    amount_to_pay -= transfer_amount
                    creditor['net_balance'] -= float(transfer_amount)
                if amount_to_pay.is_zero():
                    break

    with transaction.atomic():
        settlement = Settlement.objects.create(
            project_id=project_id,
            period_from=from_date,
            period_to=to_date,
            pre_balances={'partners': partner_details},
            details={'required_transfers': transfers}
        )

    return settlement
