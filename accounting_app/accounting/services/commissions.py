"""
Commission Tracking Service
Handles broker commissions calculation and payment tracking.
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from accounting.models import BrokerDue, PaymentVoucher, Safe
from core.feature_flags import LEGACY_COMMISSION_TRACKING_ENABLED


class CommissionService:
    """
    Service for managing broker commissions.
    """
    
    @staticmethod
    def calculate_commission(contract_value: Decimal, commission_percent: Decimal) -> Decimal:
        """
        Calculate commission amount based on contract value and percentage.
        """
        if not LEGACY_COMMISSION_TRACKING_ENABLED:
            return Decimal('0')
            
        commission = (contract_value * commission_percent / 100).quantize(Decimal('0.01'))
        return commission
    
    @staticmethod
    @transaction.atomic
    def pay_broker_due(broker_due: BrokerDue, safe: Safe) -> PaymentVoucher:
        """
        Process payment of a broker commission.
        """
        if broker_due.status != BrokerDue.Status.DUE:
            raise ValueError("هذه العمولة غير صالحة للدفع")
            
        if safe.balance < broker_due.amount:
            raise ValueError(f"رصيد الخزنة '{safe.name}' غير كافٍ")
        
        # Update safe balance
        safe.balance -= broker_due.amount
        safe.save()
        
        # Update broker due status
        broker_due.status = BrokerDue.Status.PAID
        broker_due.payment_date = timezone.now().date()
        broker_due.paid_from_safe = safe
        broker_due.save()
        
        # Create payment voucher
        unit = broker_due.contract.unit
        voucher = PaymentVoucher.objects.create(
            safe=safe,
            amount=broker_due.amount,
            voucher_date=timezone.now().date(),
            description=f"صرف عمولة سمسار للوحدة {unit.name}",
            voucher_type='broker_commission',
            reference_id=broker_due.id,
            beneficiary=broker_due.broker_name
        )
        
        return voucher
    
    @staticmethod
    def get_broker_statistics(broker_name: str):
        """
        Get statistics for a specific broker.
        """
        dues = BrokerDue.objects.filter(broker_name=broker_name)
        
        due_amount = dues.filter(status=BrokerDue.Status.DUE).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        
        paid_amount = dues.filter(status=BrokerDue.Status.PAID).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        
        return {
            'broker_name': broker_name,
            'total_due': due_amount,
            'total_paid': paid_amount,
            'total_earned': due_amount + paid_amount,
            'dues_count': dues.filter(status=BrokerDue.Status.DUE).count(),
            'paid_count': dues.filter(status=BrokerDue.Status.PAID).count(),
        }
    
    @staticmethod
    def get_all_brokers_summary():
        """
        Get summary of all brokers with their commissions.
        """
        from django.db.models import Sum, Count, Q
        
        # Get unique broker names
        broker_names = BrokerDue.objects.values_list(
            'broker_name', flat=True
        ).distinct()
        
        summaries = []
        for name in broker_names:
            if name:  # Skip empty names
                summary = CommissionService.get_broker_statistics(name)
                summaries.append(summary)
        
        # Sort by total earned descending
        summaries.sort(key=lambda x: x['total_earned'], reverse=True)
        
        return summaries