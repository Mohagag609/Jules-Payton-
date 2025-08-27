from decimal import Decimal
from django.test import TestCase
from datetime import date

from accounting.models import Customer, Unit, Contract
from accounting.services.contracts import generate_installments_for_contract

class ContractServicesTest(TestCase):

    def setUp(self):
        """Set up a customer and a unit for testing."""
        self.customer = Customer.objects.create(code='C001', name='Test Customer')
        self.unit = Unit.objects.create(code='U001', name='Test Unit', price_total=100000)

    def test_generate_installments_perfect_division(self):
        """
        Tests installment generation when the total amount is perfectly divisible.
        """
        contract = Contract.objects.create(
            code='CTR-01', customer=self.customer, unit=self.unit,
            unit_value=100000, down_payment=20000,
            installments_count=10, schedule_type='monthly', start_date=date(2024, 1, 1)
        )
        generate_installments_for_contract(contract)

        self.assertEqual(contract.installments.count(), 10)
        self.assertTrue(all(inst.amount == Decimal('8000.00') for inst in contract.installments.all()))
        total_installments_amount = sum(inst.amount for inst in contract.installments.all())
        self.assertEqual(total_installments_amount, contract.remaining_amount)

    def test_generate_installments_with_rounding(self):
        """
        Tests installment generation when rounding is required.
        The remainder should be added to the final installment.
        """
        # 1000 / 3 = 333.33, with a remainder of 0.01
        contract = Contract.objects.create(
            code='CTR-02', customer=self.customer, unit=self.unit,
            unit_value=1000, down_payment=0,
            installments_count=3, schedule_type='monthly', start_date=date(2024, 1, 1)
        )
        generate_installments_for_contract(contract)

        self.assertEqual(contract.installments.count(), 3)

        installments = contract.installments.order_by('seq_no')
        self.assertEqual(installments[0].amount, Decimal('333.33'))
        self.assertEqual(installments[1].amount, Decimal('333.33'))
        self.assertEqual(installments[2].amount, Decimal('333.34')) # 333.33 + 0.01 remainder

        total_installments_amount = sum(inst.amount for inst in installments)
        self.assertEqual(total_installments_amount, contract.remaining_amount)

    def test_due_date_calculation(self):
        """
        Tests that due dates are calculated correctly based on schedule type.
        """
        # Monthly
        contract_monthly = Contract.objects.create(
            code='CTR-M', customer=self.customer, unit=self.unit,
            unit_value=1200, down_payment=0,
            installments_count=2, schedule_type='monthly', start_date=date(2024, 1, 15)
        )
        generate_installments_for_contract(contract_monthly)
        installments_m = contract_monthly.installments.order_by('seq_no')
        self.assertEqual(installments_m[0].due_date, date(2024, 1, 15))
        self.assertEqual(installments_m[1].due_date, date(2024, 2, 15))

        # Quarterly
        contract_quarterly = Contract.objects.create(
            code='CTR-Q', customer=self.customer, unit=Unit.objects.create(code='U002', name='Q', price_total=1200),
            unit_value=1200, down_payment=0,
            installments_count=2, schedule_type='quarterly', start_date=date(2024, 1, 15)
        )
        generate_installments_for_contract(contract_quarterly)
        installments_q = contract_quarterly.installments.order_by('seq_no')
        self.assertEqual(installments_q[0].due_date, date(2024, 1, 15))
        self.assertEqual(installments_q[1].due_date, date(2024, 4, 15))

        # Yearly
        contract_yearly = Contract.objects.create(
            code='CTR-Y', customer=self.customer, unit=Unit.objects.create(code='U003', name='Y', price_total=1200),
            unit_value=1200, down_payment=0,
            installments_count=2, schedule_type='yearly', start_date=date(2024, 1, 15)
        )
        generate_installments_for_contract(contract_yearly)
        installments_y = contract_yearly.installments.order_by('seq_no')
        self.assertEqual(installments_y[0].due_date, date(2024, 1, 15))
        self.assertEqual(installments_y[1].due_date, date(2025, 1, 15))
