# Generated manually for missing Installment fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0006_add_missing_contract_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='installment',
            name='type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('regular', 'قسط عادي'),
                    ('annual', 'دفعة سنوية'),
                    ('maintenance', 'صيانة'),
                ],
                default='regular',
                verbose_name='النوع'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installment',
            name='original_amount',
            field=models.DecimalField(
                max_digits=15,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='المبلغ الأصلي'
            ),
            preserve_default=True,
        ),
    ]