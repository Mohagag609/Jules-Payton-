import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from accounting.models import *
from accounting.services.contracts import generate_installments_for_contract

class Command(BaseCommand):
    help = 'Seeds the database with demo data for the accounting app.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Clean up existing data
        self.stdout.write('Deleting existing data...')
        Contract.objects.all().delete()
        Unit.objects.all().delete()
        Customer.objects.all().delete()
        Supplier.objects.all().delete()
        PartnersGroup.objects.all().delete()
        Partner.objects.all().delete()
        Safe.objects.all().delete()
        Project.objects.all().delete()
        Item.objects.all().delete()

        # --- Create Partners and Groups ---
        self.stdout.write('Creating partners and groups...')
        partner1 = Partner.objects.create(code='P001', name='شريك ألف', share_percent=50, opening_balance=100000)
        partner2 = Partner.objects.create(code='P002', name='شريك باء', share_percent=50, opening_balance=100000)
        group = PartnersGroup.objects.create(name='المجموعة الرئيسية')
        PartnersGroupMember.objects.create(group=group, partner=partner1, percent=50)
        PartnersGroupMember.objects.create(group=group, partner=partner2, percent=50)

        # --- Create Safes ---
        self.stdout.write('Creating safes...')
        safe_main = Safe.objects.create(name='الخزنة الرئيسية')
        wallet_p1 = Safe.objects.create(name=f'محفظة {partner1.name}', is_partner_wallet=True, partner=partner1)

        # --- Create Customers and Suppliers ---
        self.stdout.write('Creating customers and suppliers...')
        customers = [Customer.objects.create(code=f'C{i:03}', name=f'عميل رقم {i}') for i in range(1, 4)]
        suppliers = [Supplier.objects.create(name=f'مورد رقم {i}') for i in range(1, 4)]

        # --- Create Units ---
        self.stdout.write('Creating units...')
        unit1 = Unit.objects.create(code='U-A101', name='شقة 101 مبنى ألف', type='residential', price_total=1200000, category='res')

        # --- Create a Contract ---
        self.stdout.write('Creating a contract...')
        contract1 = Contract.objects.create(
            code='CTR-2024-001',
            customer=customers[0],
            unit=unit1,
            unit_value=1200000,
            down_payment=200000,
            installments_count=24,
            schedule_type='monthly',
            start_date=date.today() + timedelta(days=30),
            partners_group=group
        )
        generate_installments_for_contract(contract1)

        # --- Create Projects and Items ---
        self.stdout.write('Creating projects and items...')
        project1 = Project.objects.create(code='PRJ01', name='مشروع بناء فيلا', type='build', start_date=date.today(), budget=500000)
        items = [
            Item.objects.create(code=f'ITM{i:03}', name=f'صنف {i}', uom='وحدة', unit_price=random.randint(10, 100))
            for i in range(1, 6)
        ]

        # --- Create Stock Moves ---
        self.stdout.write('Creating stock moves...')
        StockMove.objects.create(item=items[0], qty=100, direction='IN', date=date.today())
        StockMove.objects.create(item=items[0], project=project1, qty=10, direction='OUT', date=date.today())

        # --- Create Vouchers ---
        self.stdout.write('Creating vouchers...')
        # 1. Down payment receipt
        ReceiptVoucher.objects.create(
            date=date.today(), amount=contract1.down_payment, safe=safe_main,
            description=f'دفعة مقدمة عقد {contract1.code}', customer=contract1.customer, contract=contract1
        )
        # 2. Random receipts
        for i in range(4):
            ReceiptVoucher.objects.create(
                date=date.today() - timedelta(days=random.randint(1, 30)),
                amount=random.randint(1000, 5000),
                safe=safe_main,
                description=f'إيراد متنوع رقم {i+1}',
                customer=random.choice(customers)
            )
        # 3. Random payments
        for i in range(5):
            PaymentVoucher.objects.create(
                date=date.today() - timedelta(days=random.randint(1, 30)),
                amount=random.randint(500, 2000),
                safe=safe_main,
                description=f'مصروف متنوع رقم {i+1}',
                supplier=random.choice(suppliers),
                project=project1 if i % 2 == 0 else None
            )

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
