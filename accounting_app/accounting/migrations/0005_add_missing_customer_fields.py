# Generated manually for missing Customer fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_add_missing_unit_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='national_id',
            field=models.CharField(
                max_length=20,
                blank=True,
                verbose_name='الرقم القومي'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customer',
            name='address',
            field=models.TextField(
                blank=True,
                verbose_name='العنوان'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customer',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('active', 'نشط'),
                    ('inactive', 'غير نشط'),
                ],
                default='active',
                verbose_name='الحالة'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customer',
            name='notes',
            field=models.TextField(
                blank=True,
                verbose_name='ملاحظات'
            ),
            preserve_default=True,
        ),
    ]