# Generated manually for missing Unit fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_unit_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('available', 'متاحة'),
                    ('sold', 'مباعة'),
                    ('reserved', 'محجوزة'),
                    ('returned', 'مرتجعة'),
                ],
                default='available',
                verbose_name='الحالة'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unit',
            name='floor',
            field=models.CharField(
                max_length=10,
                blank=True,
                verbose_name='الطابق'
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unit',
            name='area',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True,
                verbose_name='المساحة (م²)'
            ),
            preserve_default=True,
        ),
    ]