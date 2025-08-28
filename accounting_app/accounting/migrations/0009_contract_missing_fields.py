# Generated manually to add missing contract fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0008_unit_notes_field'),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE accounting_contract 
            ADD COLUMN IF NOT EXISTS broker_name VARCHAR(255) DEFAULT '',
            ADD COLUMN IF NOT EXISTS broker_percent DECIMAL(5,2) DEFAULT 0,
            ADD COLUMN IF NOT EXISTS broker_amount DECIMAL(15,2) DEFAULT 0,
            ADD COLUMN IF NOT EXISTS commission_safe_id INTEGER,
            ADD COLUMN IF NOT EXISTS discount_amount DECIMAL(15,2) DEFAULT 0,
            ADD COLUMN IF NOT EXISTS discount_percent DECIMAL(5,2) DEFAULT 0,
            ADD COLUMN IF NOT EXISTS final_amount DECIMAL(15,2) DEFAULT 0,
            ADD COLUMN IF NOT EXISTS commission_notes TEXT DEFAULT '',
            ADD COLUMN IF NOT EXISTS notes TEXT DEFAULT '';
            """,
            reverse_sql="""
            ALTER TABLE accounting_contract 
            DROP COLUMN IF EXISTS broker_name,
            DROP COLUMN IF EXISTS broker_percent,
            DROP COLUMN IF EXISTS broker_amount,
            DROP COLUMN IF EXISTS commission_safe_id,
            DROP COLUMN IF EXISTS discount_amount,
            DROP COLUMN IF EXISTS discount_percent,
            DROP COLUMN IF EXISTS final_amount,
            DROP COLUMN IF EXISTS commission_notes,
            DROP COLUMN IF EXISTS notes;
            """
        ),
    ]