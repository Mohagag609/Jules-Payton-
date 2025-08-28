# Generated manually to add remaining contract fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0010_add_all_missing_columns'),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE accounting_contract 
            ADD COLUMN IF NOT EXISTS maintenance_deposit DECIMAL(15,2) DEFAULT 0,
            ADD COLUMN IF NOT EXISTS extra_annual INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS annual_payment_value DECIMAL(15,2) DEFAULT 0;
            """,
            reverse_sql="""
            ALTER TABLE accounting_contract 
            DROP COLUMN IF EXISTS maintenance_deposit,
            DROP COLUMN IF EXISTS extra_annual,
            DROP COLUMN IF EXISTS annual_payment_value;
            """
        ),
    ]