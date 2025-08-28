# Generated manually to add missing notes field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0007_merge_20250828_1853'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE accounting_unit ADD COLUMN IF NOT EXISTS notes TEXT DEFAULT '';",
            reverse_sql="ALTER TABLE accounting_unit DROP COLUMN IF EXISTS notes;"
        ),
    ]