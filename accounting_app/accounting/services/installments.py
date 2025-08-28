"""
Smart Installments Generation Service
Handles the complex logic for creating installments with various payment types.
"""

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.db import transaction
from accounting.models import Installment, Contract, BrokerDue
from core.feature_flags import LEGACY_SMART_INSTALLMENTS_ENABLED


class InstallmentGeneratorService:
    """
    Service for generating smart installments based on contract terms.
    """
    
    SCHEDULE_MONTHS = {
        Contract.ScheduleType.MONTHLY: 1,
        Contract.ScheduleType.QUARTERLY: 3,
        Contract.ScheduleType.YEARLY: 12,
    }
    
    def __init__(self, contract: Contract):
        self.contract = contract
        
    @transaction.atomic
    def generate_installments(self):
        """
        Generate all installments for a contract including:
        - Regular installments
        - Annual bonus payments
        - Maintenance deposit
        """
        if not LEGACY_SMART_INSTALLMENTS_ENABLED:
            return self._generate_simple_installments()
            
        # Clear existing installments
        self.contract.installments.all().delete()
        
        # Calculate amounts
        installment_base = self.contract.unit_value - (self.contract.maintenance_deposit or 0)
        total_after_down = installment_base - self.contract.discount_amount - self.contract.down_payment
        
        if total_after_down < 0:
            raise ValueError("المقدم والخصم أكبر من قيمة العقد الخاضعة للتقسيط")
        
        # Calculate annual payments total
        total_annual_payments = self.contract.extra_annual * self.contract.annual_payment_value
        
        if total_annual_payments > total_after_down:
            raise ValueError("مجموع الدفعات السنوية أكبر من المبلغ المتبقي للتقسيط")
        
        # Amount for regular installments
        amount_for_regular = total_after_down - total_annual_payments
        
        installments = []
        seq_no = 1
        
        # Generate regular installments
        if self.contract.installments_count > 0 and amount_for_regular > 0:
            regular_installments = self._generate_regular_installments(
                amount_for_regular, 
                seq_no
            )
            installments.extend(regular_installments)
            seq_no += len(regular_installments)
        
        # Generate annual bonus installments
        if self.contract.extra_annual > 0:
            annual_installments = self._generate_annual_installments(seq_no)
            installments.extend(annual_installments)
            seq_no += len(annual_installments)
        
        # Generate maintenance deposit installment
        if self.contract.maintenance_deposit > 0:
            maintenance_installment = self._generate_maintenance_installment(seq_no)
            installments.append(maintenance_installment)
        
        # Save all installments
        Installment.objects.bulk_create(installments)
        
        # Generate broker due if applicable
        self._generate_broker_due()
        
        return installments
    
    def _generate_regular_installments(self, total_amount, start_seq):
        """Generate regular monthly/quarterly/yearly installments."""
        installments = []
        count = self.contract.installments_count
        base_amount = Decimal(str(total_amount / count))
        base_amount = base_amount.quantize(Decimal('0.01'))  # Round to 2 decimals
        
        accumulated = Decimal('0')
        months = self.SCHEDULE_MONTHS[self.contract.schedule_type]
        
        for i in range(count):
            due_date = self.contract.start_date + relativedelta(months=months * (i + 1))
            
            # Last installment gets the remainder
            if i == count - 1:
                amount = total_amount - accumulated
            else:
                amount = base_amount
                accumulated += amount
            
            installment = Installment(
                contract=self.contract,
                seq_no=start_seq + i,
                due_date=due_date,
                amount=amount,
                type=Installment.InstallmentType.REGULAR
            )
            installments.append(installment)
        
        return installments
    
    def _generate_annual_installments(self, start_seq):
        """Generate annual bonus installments."""
        installments = []
        
        for i in range(self.contract.extra_annual):
            due_date = self.contract.start_date + relativedelta(years=i + 1)
            
            installment = Installment(
                contract=self.contract,
                seq_no=start_seq + i,
                due_date=due_date,
                amount=self.contract.annual_payment_value,
                type=Installment.InstallmentType.ANNUAL
            )
            installments.append(installment)
        
        return installments
    
    def _generate_maintenance_installment(self, seq_no):
        """Generate maintenance deposit installment."""
        # Get the last installment date
        last_installment = self.contract.installments.order_by('-due_date').first()
        
        if last_installment:
            # Set maintenance due date one period after the last installment
            months = self.SCHEDULE_MONTHS.get(self.contract.schedule_type, 12)
            due_date = last_installment.due_date + relativedelta(months=months)
        else:
            # If no other installments, set it one year from start
            due_date = self.contract.start_date + relativedelta(years=1)
        
        return Installment(
            contract=self.contract,
            seq_no=seq_no,
            due_date=due_date,
            amount=self.contract.maintenance_deposit,
            type=Installment.InstallmentType.MAINTENANCE
        )
    
    def _generate_broker_due(self):
        """Generate broker commission due if applicable."""
        if self.contract.broker_amount > 0:
            BrokerDue.objects.create(
                contract=self.contract,
                broker_name=self.contract.broker_name or 'سمسار غير محدد',
                amount=self.contract.broker_amount,
                due_date=self.contract.start_date,
                status=BrokerDue.Status.DUE
            )
    
    def _generate_simple_installments(self):
        """Simple installment generation without legacy features."""
        count = self.contract.installments_count
        remaining = self.contract.remaining_amount
        amount_per_installment = remaining / count
        
        installments = []
        months = self.SCHEDULE_MONTHS[self.contract.schedule_type]
        
        for i in range(count):
            due_date = self.contract.start_date + relativedelta(months=months * (i + 1))
            
            installment = Installment(
                contract=self.contract,
                seq_no=i + 1,
                due_date=due_date,
                amount=amount_per_installment,
                type=Installment.InstallmentType.REGULAR
            )
            installments.append(installment)
        
        return Installment.objects.bulk_create(installments)