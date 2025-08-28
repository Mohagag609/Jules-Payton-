# Generated manually - Add missing fields with safety checks

from django.db import migrations, connection


def safe_add_fields(apps, schema_editor):
    """Add fields only if they don't exist"""
    
    with connection.cursor() as cursor:
        # Check and add Customer fields
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'accounting_customer'
        """)
        customer_columns = [row[0] for row in cursor.fetchall()]
        
        if 'national_id' not in customer_columns:
            cursor.execute("""
                ALTER TABLE accounting_customer 
                ADD COLUMN national_id VARCHAR(20) DEFAULT ''
            """)
        
        if 'address' not in customer_columns:
            cursor.execute("""
                ALTER TABLE accounting_customer 
                ADD COLUMN address TEXT DEFAULT ''
            """)
        
        if 'status' not in customer_columns:
            cursor.execute("""
                ALTER TABLE accounting_customer 
                ADD COLUMN status VARCHAR(20) DEFAULT 'active'
            """)
        
        if 'notes' not in customer_columns:
            cursor.execute("""
                ALTER TABLE accounting_customer 
                ADD COLUMN notes TEXT DEFAULT ''
            """)
        
        # Check and add Contract fields
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'accounting_contract'
        """)
        contract_columns = [row[0] for row in cursor.fetchall()]
        
        if 'commission_rate' not in contract_columns:
            cursor.execute("""
                ALTER TABLE accounting_contract 
                ADD COLUMN commission_rate DECIMAL(5,2) DEFAULT 0
            """)
        
        if 'annual_payment_date' not in contract_columns:
            cursor.execute("""
                ALTER TABLE accounting_contract 
                ADD COLUMN annual_payment_date DATE NULL
            """)
        
        # Check and add Installment fields
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'accounting_installment'
        """)
        installment_columns = [row[0] for row in cursor.fetchall()]
        
        if 'type' not in installment_columns:
            cursor.execute("""
                ALTER TABLE accounting_installment 
                ADD COLUMN type VARCHAR(20) DEFAULT 'regular'
            """)
        
        if 'original_amount' not in installment_columns:
            cursor.execute("""
                ALTER TABLE accounting_installment 
                ADD COLUMN original_amount DECIMAL(15,2) NULL
            """)


def reverse_func(apps, schema_editor):
    """Reverse migration - do nothing as we don't want to drop columns"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_add_missing_unit_fields'),
    ]

    operations = [
        migrations.RunPython(safe_add_fields, reverse_func),
    ]