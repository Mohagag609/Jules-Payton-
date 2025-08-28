# Generated manually for missing Contract fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_add_missing_customer_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='commission_rate',
            field=models.DecimalField(
                max_digits=5,
                decimal_places=2,
                default=0,
                verbose_name='نسبة العمولة %'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contract',
            name='annual_payment_date',
            field=models.DateField(
                null=True,
                blank=True,
                verbose_name='تاريخ الدفعة السنوية'
            ),
            preserve_default=True,
        ),
    ]