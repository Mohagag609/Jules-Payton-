# Generated manually to add all potentially missing columns

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0009_contract_missing_fields'),
    ]

    operations = [
        # Customer missing fields
        migrations.RunSQL(
            """
            ALTER TABLE accounting_customer 
            ADD COLUMN IF NOT EXISTS email VARCHAR(254) DEFAULT '',
            ADD COLUMN IF NOT EXISTS notes TEXT DEFAULT '';
            """,
            reverse_sql=""
        ),
        
        # Partner missing fields
        migrations.RunSQL(
            """
            ALTER TABLE accounting_partner 
            ADD COLUMN IF NOT EXISTS notes TEXT DEFAULT '';
            """,
            reverse_sql=""
        ),
        
        # Safe missing fields
        migrations.RunSQL(
            """
            ALTER TABLE accounting_safe 
            ADD COLUMN IF NOT EXISTS notes TEXT DEFAULT '';
            """,
            reverse_sql=""
        ),
        
        # Contract created_at field
        migrations.RunSQL(
            """
            ALTER TABLE accounting_contract 
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """,
            reverse_sql=""
        ),
    ]