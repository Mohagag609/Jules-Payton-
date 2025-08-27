from decimal import Decimal
from django.test import TestCase
from datetime import date

from accounting.models import Safe, ReceiptVoucher, PaymentVoucher
from accounting.services.treasury import get_safe_balance

class VoucherAndSafeBalanceTest(TestCase):

    def setUp(self):
        """Set up a safe for testing."""
        self.safe = Safe.objects.create(name='Main Safe')

    def test_initial_safe_balance(self):
        """Tests that a new safe has a balance of zero."""
        balance = get_safe_balance(self.safe)
        self.assertEqual(balance, Decimal('0.00'))

    def test_receipt_voucher_increases_balance(self):
        """Tests that a receipt voucher increases the safe's balance."""
        ReceiptVoucher.objects.create(
            date=date.today(),
            amount=Decimal('500.00'),
            safe=self.safe,
            description='Test receipt'
        )
        balance = get_safe_balance(self.safe)
        self.assertEqual(balance, Decimal('500.00'))

    def test_payment_voucher_decreases_balance(self):
        """Tests that a payment voucher decreases the safe's balance."""
        PaymentVoucher.objects.create(
            date=date.today(),
            amount=Decimal('200.00'),
            safe=self.safe,
            description='Test payment'
        )
        balance = get_safe_balance(self.safe)
        self.assertEqual(balance, Decimal('-200.00'))

    def test_multiple_vouchers_correct_balance(self):
        """Tests the balance calculation with multiple vouchers."""
        ReceiptVoucher.objects.create(date=date.today(), amount=1000, safe=self.safe, description='R1')
        PaymentVoucher.objects.create(date=date.today(), amount=300, safe=self.safe, description='P1')
        ReceiptVoucher.objects.create(date=date.today(), amount=50, safe=self.safe, description='R2')
        PaymentVoucher.objects.create(date=date.today(), amount=150, safe=self.safe, description='P2')

        # Expected balance: 1000 - 300 + 50 - 150 = 600
        balance = get_safe_balance(self.safe)
        self.assertEqual(balance, Decimal('600.00'))

    def test_balance_calculation_with_date_filter(self):
        """Tests that the balance is calculated correctly up to a certain date."""
        ReceiptVoucher.objects.create(date=date(2024, 1, 10), amount=1000, safe=self.safe, description='R1')
        PaymentVoucher.objects.create(date=date(2024, 1, 15), amount=200, safe=self.safe, description='P1')
        ReceiptVoucher.objects.create(date=date(2024, 2, 5), amount=500, safe=self.safe, description='R2')

        # Balance at the end of January
        balance_jan = get_safe_balance(self.safe, to_date=date(2024, 1, 31))
        self.assertEqual(balance_jan, Decimal('800.00')) # 1000 - 200

        # Balance at the end of February
        balance_feb = get_safe_balance(self.safe, to_date=date(2024, 2, 29))
        self.assertEqual(balance_feb, Decimal('1300.00')) # 800 + 500
