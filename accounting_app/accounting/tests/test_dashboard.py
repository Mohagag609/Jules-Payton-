from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta

from accounting.models import ReceiptVoucher, PaymentVoucher, Installment, Safe, Customer, Unit, Contract

class DashboardViewTest(TestCase):

    def setUp(self):
        """Set up data for dashboard KPI testing."""
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        self.safe = Safe.objects.create(name='Test Safe')
        customer = Customer.objects.create(code='C001', name='Test Customer')
        unit = Unit.objects.create(code='U001', name='Test Unit', price_total=1000)
        contract = Contract.objects.create(
            code='CTR-01', customer=customer, unit=unit,
            unit_value=1000, down_payment=0,
            installments_count=2, schedule_type='monthly', start_date=date.today()
        )

        # Total Receipts = 500 + 300 = 800
        ReceiptVoucher.objects.create(date=date.today(), amount=500, safe=self.safe, description='R1')
        ReceiptVoucher.objects.create(date=date.today(), amount=300, safe=self.safe, description='R2')

        # Total Payments = 100 + 50 = 150
        PaymentVoucher.objects.create(date=date.today(), amount=100, safe=self.safe, description='P1')
        PaymentVoucher.objects.create(date=date.today(), amount=50, safe=self.safe, description='P2')

        # Net Balance = 800 - 150 = 650

        # Late Installments = 2
        Installment.objects.create(
            contract=contract, seq_no=1, due_date=date.today() - timedelta(days=10),
            amount=500, status='PENDING'
        )
        Installment.objects.create(
            contract=contract, seq_no=2, due_date=date.today() - timedelta(days=5),
            amount=500, status='PENDING'
        )
        # This one is not late
        Installment.objects.create(
            contract=contract, seq_no=3, due_date=date.today() + timedelta(days=5),
            amount=500, status='PENDING'
        )

    def test_dashboard_kpis(self):
        """
        Tests that the KPIs rendered in the dashboard context are correct.
        """
        response = self.client.get(reverse('accounting:dashboard'))
        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertEqual(context['total_receipts'], Decimal('800.00'))
        self.assertEqual(context['total_payments'], Decimal('150.00'))
        self.assertEqual(context['net_balance'], Decimal('650.00'))

        # The view logic updates the status of installments before counting.
        # So we expect the count to be correct.
        self.assertEqual(context['late_installments_count'], 2)

    def test_dashboard_requires_login(self):
        """
        Tests that the dashboard is not accessible to anonymous users.
        """
        self.client.logout()
        response = self.client.get(reverse('accounting:dashboard'))
        self.assertEqual(response.status_code, 302) # Redirect to login
        self.assertIn('/admin/login/', response.url)
