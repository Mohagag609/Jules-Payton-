"""
Partner Profits Calculation Service
Handles complex profit distribution based on ownership percentages.
"""

from decimal import Decimal
from django.db.models import Sum, Q, F
from django.utils import timezone
from datetime import datetime, timedelta

from accounting.models import (
    Partner, UnitPartner, Contract, ReceiptVoucher, 
    PaymentVoucher, PartnerDebt, BrokerDue
)


class PartnerProfitService:
    """
    Service for calculating and tracking partner profits.
    """
    
    @staticmethod
    def calculate_partner_ledger(partner_id, from_date=None, to_date=None):
        """
        Generate a complete ledger for a partner including all income and expenses.
        """
        partner = Partner.objects.get(id=partner_id)
        transactions = []
        
        # Date filtering
        date_filter = Q()
        if from_date:
            date_filter &= Q(voucher_date__gte=from_date)
        if to_date:
            date_filter &= Q(voucher_date__lte=to_date)
        
        # Get all units where this partner has ownership
        unit_partnerships = UnitPartner.objects.filter(
            partner_id=partner_id
        ).select_related('unit')
        
        # Process receipts (income)
        for partnership in unit_partnerships:
            # Get contract for this unit
            try:
                contract = Contract.objects.get(unit=partnership.unit)
            except Contract.DoesNotExist:
                continue
            
            # Get all receipts for this contract
            receipts = ReceiptVoucher.objects.filter(
                Q(reference_id=contract.id) | 
                Q(reference_id__in=contract.installments.values_list('id', flat=True)),
                voucher_type__in=['contract_payment', 'installment_payment']
            )
            
            if date_filter:
                receipts = receipts.filter(date_filter)
            
            for receipt in receipts:
                partner_share = (receipt.amount * partnership.percent / 100)
                transactions.append({
                    'date': receipt.voucher_date,
                    'type': 'income',
                    'description': f"حصة من {receipt.description} - الوحدة {partnership.unit.name}",
                    'unit': partnership.unit,
                    'amount': partner_share,
                    'income': partner_share,
                    'expense': Decimal('0'),
                    'reference': receipt,
                    'percent': partnership.percent
                })
        
        # Process broker commissions (expenses)
        for partnership in unit_partnerships:
            try:
                contract = Contract.objects.get(unit=partnership.unit)
            except Contract.DoesNotExist:
                continue
            
            # Get paid broker dues
            broker_dues = BrokerDue.objects.filter(
                contract=contract,
                status='paid'
            )
            
            if from_date:
                broker_dues = broker_dues.filter(payment_date__gte=from_date)
            if to_date:
                broker_dues = broker_dues.filter(payment_date__lte=to_date)
            
            for due in broker_dues:
                partner_share = (due.amount * partnership.percent / 100)
                transactions.append({
                    'date': due.payment_date,
                    'type': 'expense',
                    'description': f"حصة من عمولة سمسار - الوحدة {partnership.unit.name}",
                    'unit': partnership.unit,
                    'amount': partner_share,
                    'income': Decimal('0'),
                    'expense': partner_share,
                    'reference': due,
                    'percent': partnership.percent
                })
        
        # Process general expenses allocated to units
        for partnership in unit_partnerships:
            # Get payments related to this unit
            payments = PaymentVoucher.objects.filter(
                reference_id=partnership.unit.id,
                voucher_type='unit_expense'
            )
            
            if date_filter:
                payments = payments.filter(date_filter)
            
            for payment in payments:
                partner_share = (payment.amount * partnership.percent / 100)
                transactions.append({
                    'date': payment.voucher_date,
                    'type': 'expense',
                    'description': f"حصة من {payment.description} - الوحدة {partnership.unit.name}",
                    'unit': partnership.unit,
                    'amount': partner_share,
                    'income': Decimal('0'),
                    'expense': partner_share,
                    'reference': payment,
                    'percent': partnership.percent
                })
        
        # Process partner debts
        # Debts owed to this partner (income when paid)
        debts_to_receive = PartnerDebt.objects.filter(
            owed_partner_id=partner_id,
            status='paid'
        )
        
        if from_date:
            debts_to_receive = debts_to_receive.filter(payment_date__gte=from_date)
        if to_date:
            debts_to_receive = debts_to_receive.filter(payment_date__lte=to_date)
        
        for debt in debts_to_receive:
            transactions.append({
                'date': debt.payment_date,
                'type': 'income',
                'description': f"تحصيل دين من {debt.paying_partner.name} - الوحدة {debt.unit.name}",
                'unit': debt.unit,
                'amount': debt.amount,
                'income': debt.amount,
                'expense': Decimal('0'),
                'reference': debt,
                'percent': Decimal('100')  # Full amount
            })
        
        # Debts owed by this partner (expense when paid)
        debts_to_pay = PartnerDebt.objects.filter(
            paying_partner_id=partner_id,
            status='paid'
        )
        
        if from_date:
            debts_to_pay = debts_to_pay.filter(payment_date__gte=from_date)
        if to_date:
            debts_to_pay = debts_to_pay.filter(payment_date__lte=to_date)
        
        for debt in debts_to_pay:
            transactions.append({
                'date': debt.payment_date,
                'type': 'expense',
                'description': f"سداد دين إلى {debt.owed_partner.name} - الوحدة {debt.unit.name}",
                'unit': debt.unit,
                'amount': debt.amount,
                'income': Decimal('0'),
                'expense': debt.amount,
                'reference': debt,
                'percent': Decimal('100')  # Full amount
            })
        
        # Sort transactions by date
        transactions.sort(key=lambda x: x['date'])
        
        # Calculate running balance
        balance = Decimal('0')
        for transaction in transactions:
            balance += transaction['income'] - transaction['expense']
            transaction['balance'] = balance
        
        # Calculate totals
        total_income = sum(t['income'] for t in transactions)
        total_expense = sum(t['expense'] for t in transactions)
        net_position = total_income - total_expense
        
        return {
            'partner': partner,
            'transactions': transactions,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_position': net_position,
            'final_balance': balance
        }
    
    @staticmethod
    def get_all_partners_summary(from_date=None, to_date=None):
        """
        Get profit summary for all active partners.
        """
        partners = Partner.objects.filter(is_active=True)
        summaries = []
        
        for partner in partners:
            ledger = PartnerProfitService.calculate_partner_ledger(
                partner.id, from_date, to_date
            )
            
            # Get unit ownership summary
            partnerships = UnitPartner.objects.filter(
                partner=partner
            ).select_related('unit')
            
            units_summary = []
            total_ownership_value = Decimal('0')
            
            for partnership in partnerships:
                unit_value = partnership.unit.price_total * partnership.percent / 100
                total_ownership_value += unit_value
                
                units_summary.append({
                    'unit': partnership.unit,
                    'percent': partnership.percent,
                    'value': unit_value
                })
            
            summaries.append({
                'partner': partner,
                'units_count': partnerships.count(),
                'units_summary': units_summary,
                'total_ownership_value': total_ownership_value,
                'total_income': ledger['total_income'],
                'total_expense': ledger['total_expense'],
                'net_profit': ledger['net_position'],
                'roi': (ledger['net_position'] / total_ownership_value * 100).quantize(Decimal('0.01')) if total_ownership_value > 0 else Decimal('0')
            })
        
        # Sort by net profit descending
        summaries.sort(key=lambda x: x['net_profit'], reverse=True)
        
        return summaries
    
    @staticmethod
    def get_monthly_profit_trend(partner_id, months=12):
        """
        Get monthly profit trend for a partner.
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30 * months)
        
        monthly_data = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_start = current_date
            month_end = (current_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            ledger = PartnerProfitService.calculate_partner_ledger(
                partner_id, month_start, month_end
            )
            
            monthly_data.append({
                'month': current_date.strftime('%Y-%m'),
                'month_display': current_date.strftime('%B %Y'),
                'income': ledger['total_income'],
                'expense': ledger['total_expense'],
                'profit': ledger['net_position']
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return monthly_data
    
    @staticmethod
    def get_unit_profitability_report():
        """
        Get profitability report for all units.
        """
        units = Unit.objects.filter(status='sold')
        report = []
        
        for unit in units:
            try:
                contract = Contract.objects.get(unit=unit)
            except Contract.DoesNotExist:
                continue
            
            # Calculate total receipts
            total_receipts = ReceiptVoucher.objects.filter(
                Q(reference_id=contract.id) | 
                Q(reference_id__in=contract.installments.values_list('id', flat=True))
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            # Calculate total expenses
            total_expenses = Decimal('0')
            
            # Broker commission
            broker_dues = BrokerDue.objects.filter(
                contract=contract,
                status='paid'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            total_expenses += broker_dues
            
            # Unit expenses
            unit_expenses = PaymentVoucher.objects.filter(
                reference_id=unit.id,
                voucher_type='unit_expense'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            total_expenses += unit_expenses
            
            # Calculate profit
            profit = total_receipts - total_expenses
            profit_margin = (profit / contract.unit_value * 100).quantize(Decimal('0.01')) if contract.unit_value > 0 else Decimal('0')
            
            # Get partners
            partnerships = UnitPartner.objects.filter(unit=unit).select_related('partner')
            
            report.append({
                'unit': unit,
                'contract': contract,
                'total_receipts': total_receipts,
                'total_expenses': total_expenses,
                'profit': profit,
                'profit_margin': profit_margin,
                'collection_rate': (total_receipts / contract.unit_value * 100).quantize(Decimal('0.01')) if contract.unit_value > 0 else Decimal('0'),
                'partnerships': partnerships
            })
        
        # Sort by profit descending
        report.sort(key=lambda x: x['profit'], reverse=True)
        
        return report