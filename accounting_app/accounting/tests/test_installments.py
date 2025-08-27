from decimal import Decimal
from django.test import TestCase
from datetime import date, timedelta
from unittest.mock import patch

from accounting.models import Customer, Unit, Contract, Installment, Safe, ReceiptVoucher
from accounting.services.installments import pay_installment

class InstallmentPaymentTest(TestCase):

    def setUp(self):
        """Set up a contract with one installment for testing."""
        customer = Customer.objects.create(code='C001', name='Test Customer')
        unit = Unit.objects.create(code='U001', name='Test Unit', price_total=1000)
        self.contract = Contract.objects.create(
            code='CTR-01', customer=customer, unit=unit,
            unit_value=1000, down_payment=0,
            installments_count=1, schedule_type='monthly', start_date=date(2024, 1, 1)
        )
        # Set due date in the future to ensure it's PENDING not LATE
        self.installment = Installment.objects.create(
            contract=self.contract, seq_no=1, due_date=date.today() + timedelta(days=30),
            amount=Decimal('1000.00'), status='PENDING'
        )
        self.safe = Safe.objects.create(name='Test Safe')

    def test_pay_full_installment(self):
        """Tests that paying an installment in full updates its status to PAID."""
        self.assertEqual(self.installment.status, 'PENDING')

        pay_installment(
            installment=self.installment,
            amount=Decimal('1000.00'),
            safe=self.safe,
            payment_date=date.today()
        )

        self.installment.refresh_from_db()
        self.assertEqual(self.installment.paid_amount, Decimal('1000.00'))
        self.assertEqual(self.installment.status, 'PAID')
        self.assertTrue(ReceiptVoucher.objects.filter(installment=self.installment).exists())
        self.assertEqual(ReceiptVoucher.objects.get(installment=self.installment).amount, Decimal('1000.00'))

    def test_pay_partial_installment(self):
        """Tests that paying a partial amount does not change the status from PENDING."""
        pay_installment(
            installment=self.installment,
            amount=Decimal('400.00'),
            safe=self.safe,
            payment_date=date.today()
        )
        self.installment.refresh_from_db()
        self.assertEqual(self.installment.paid_amount, Decimal('400.00'))
        self.assertEqual(self.installment.status, 'PENDING')

    def test_status_updates_to_late(self):
        """
        Tests that the installment status becomes LATE if the due date has passed.
        """
        # Create an installment with a due date in the past
        late_installment = Installment.objects.create(
            contract=self.contract, seq_no=2, due_date=date.today() - timedelta(days=1),
            amount=Decimal('100.00'), status='PENDING'
        )

        late_installment.update_status()
        self.assertEqual(late_installment.status, 'LATE')

    def test_partial_payment_on_late_installment(self):
        """
        Tests that a partial payment on a late installment keeps the status as LATE.
        """
        late_installment = Installment.objects.create(
            contract=self.contract, seq_no=2, due_date=date.today() - timedelta(days=1),
            amount=Decimal('500.00'), status='PENDING'
        )
        late_installment.update_status() # It's now LATE
        self.assertEqual(late_installment.status, 'LATE')

        pay_installment(
            installment=late_installment,
            amount=Decimal('250.00'),
            safe=self.safe,
            payment_date=date.today()
        )
        late_installment.refresh_from_db()
        self.assertEqual(late_installment.status, 'LATE') # Still LATE because it's not fully paid

        # Now pay the rest
        pay_installment(
            installment=late_installment,
            amount=Decimal('250.00'),
            safe=self.safe,
            payment_date=date.today()
        )
        late_installment.refresh_from_db()
        self.assertEqual(late_installment.status, 'PAID') # Now it's PAID
        self.assertEqual(late_installment.paid_amount, Decimal('500.00'))
