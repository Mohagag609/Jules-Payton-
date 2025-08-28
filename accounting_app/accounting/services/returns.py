"""
Unit Return and Partner Buyout Service
Handles complex unit return process with partner debt creation.
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from accounting.models import (
    Unit, Contract, Installment, UnitPartner, PartnerDebt,
    ReceiptVoucher, PaymentVoucher, AuditLog
)
from accounting.services.audit import AuditService
from core.feature_flags import LEGACY_PARTNER_RETURN_ENABLED


class UnitReturnService:
    """
    Service for handling unit returns and partner buyouts.
    """
    
    def __init__(self, unit: Unit, buying_partner_id: int):
        self.unit = unit
        self.buying_partner_id = buying_partner_id
        self.contract = None
        self.original_partners = []
        self.errors = []
        
    def validate(self):
        """
        Validate if the return process can be executed.
        """
        if not LEGACY_PARTNER_RETURN_ENABLED:
            self.errors.append("عملية إرجاع الوحدات غير مفعلة حالياً")
            return False
            
        # Check unit status
        if self.unit.status != 'sold':
            self.errors.append("يمكن تنفيذ هذه العملية على الوحدات المباعة فقط")
            return False
            
        # Get contract
        try:
            self.contract = Contract.objects.get(unit=self.unit)
        except Contract.DoesNotExist:
            self.errors.append("لم يتم العثور على عقد لهذه الوحدة")
            return False
            
        # Get original partners
        self.original_partners = list(UnitPartner.objects.filter(unit=self.unit))
        if not self.original_partners:
            self.errors.append("لا يوجد شركاء مرتبطون بهذه الوحدة")
            return False
            
        # Check if buying partner is one of the original partners
        partner_ids = [up.partner_id for up in self.original_partners]
        if self.buying_partner_id not in partner_ids:
            self.errors.append("الشريك المشتري يجب أن يكون أحد الشركاء الأصليين")
            return False
            
        return True
    
    @transaction.atomic
    def execute(self, user=None):
        """
        Execute the unit return and partner buyout process.
        """
        if not self.validate():
            raise ValueError("; ".join(self.errors))
            
        # Log the action
        AuditService.log_action(
            user=user,
            action=AuditLog.Action.OTHER,
            description=f"بدء عملية إرجاع الوحدة {self.unit.name} وشراء الشريك",
            obj=self.unit,
            details={
                'buying_partner_id': self.buying_partner_id,
                'contract_id': self.contract.id,
                'original_partners': [
                    {'partner_id': up.partner_id, 'percent': float(up.percent)}
                    for up in self.original_partners
                ]
            }
        )
        
        # 1. Change unit status back to available
        self.unit.status = 'available'
        self.unit.save()
        
        # 2. Cancel unpaid installments
        unpaid_installments = Installment.objects.filter(
            contract=self.contract,
            status__in=['PENDING', 'LATE', 'PARTIAL']
        )
        cancelled_count = unpaid_installments.count()
        unpaid_installments.delete()
        
        # 3. Get payment schedule for debt creation
        all_installments = list(Installment.objects.filter(
            contract=self.contract
        ).order_by('due_date'))
        
        # 4. Create partner debts
        selling_partners = [
            up for up in self.original_partners 
            if up.partner_id != self.buying_partner_id
        ]
        
        created_debts = []
        for seller in selling_partners:
            debts = self._create_partner_debts(
                seller, 
                all_installments,
                self.contract.unit_value
            )
            created_debts.extend(debts)
        
        # 5. Update unit ownership to 100% for buying partner
        UnitPartner.objects.filter(unit=self.unit).delete()
        UnitPartner.objects.create(
            unit=self.unit,
            partner_id=self.buying_partner_id,
            percent=Decimal('100.00')
        )
        
        # 6. Mark contract as cancelled
        self.contract.status = 'cancelled'
        self.contract.cancellation_date = timezone.now().date()
        self.contract.cancellation_reason = f"إرجاع وشراء من قبل الشريك ID: {self.buying_partner_id}"
        self.contract.save()
        
        # Log completion
        AuditService.log_action(
            user=user,
            action=AuditLog.Action.UPDATE,
            description=f"اكتمال عملية إرجاع الوحدة {self.unit.name}",
            obj=self.unit,
            details={
                'cancelled_installments': cancelled_count,
                'created_debts': len(created_debts),
                'new_owner_id': self.buying_partner_id,
                'new_owner_percent': 100
            }
        )
        
        return {
            'success': True,
            'unit': self.unit,
            'contract': self.contract,
            'cancelled_installments': cancelled_count,
            'created_debts': created_debts,
            'message': 'تمت عملية الإرجاع وشراء الشريك بنجاح'
        }
    
    def _create_partner_debts(self, seller_partnership, installments, total_value):
        """
        Create partner debts based on installment schedule.
        """
        if not installments:
            return []
            
        # Calculate debt owed
        debt_owed = (total_value * seller_partnership.percent / 100)
        
        # Calculate installment amounts
        num_installments = len(installments)
        installment_amount = (debt_owed / num_installments).quantize(Decimal('0.01'))
        
        debts = []
        accumulated_amount = Decimal('0')
        
        for i, inst in enumerate(installments):
            # Last installment gets the remainder
            if i == num_installments - 1:
                amount = debt_owed - accumulated_amount
            else:
                amount = installment_amount
                accumulated_amount += amount
            
            debt = PartnerDebt.objects.create(
                unit=self.unit,
                paying_partner_id=self.buying_partner_id,
                owed_partner_id=seller_partnership.partner_id,
                amount=amount,
                due_date=inst.due_date,
                status='unpaid',
                notes=f"دين ناتج عن إرجاع الوحدة {self.unit.name}"
            )
            debts.append(debt)
        
        return debts
    
    @staticmethod
    def get_return_preview(unit: Unit, buying_partner_id: int):
        """
        Get a preview of what will happen if the return is executed.
        """
        service = UnitReturnService(unit, buying_partner_id)
        
        if not service.validate():
            return {
                'success': False,
                'errors': service.errors
            }
        
        # Calculate what would happen
        selling_partners = [
            up for up in service.original_partners 
            if up.partner_id != buying_partner_id
        ]
        
        total_debt = Decimal('0')
        partner_debts = []
        
        for seller in selling_partners:
            debt_amount = (service.contract.unit_value * seller.percent / 100)
            total_debt += debt_amount
            partner_debts.append({
                'partner': seller.partner,
                'percent': seller.percent,
                'debt_amount': debt_amount
            })
        
        unpaid_installments = Installment.objects.filter(
            contract=service.contract,
            status__in=['PENDING', 'LATE', 'PARTIAL']
        ).count()
        
        return {
            'success': True,
            'unit': service.unit,
            'contract': service.contract,
            'buying_partner_id': buying_partner_id,
            'total_debt': total_debt,
            'partner_debts': partner_debts,
            'installments_to_cancel': unpaid_installments
        }