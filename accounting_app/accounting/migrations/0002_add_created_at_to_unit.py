# Generated manually for Render deployment

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء', null=True),
            preserve_default=False,
        ),
    ]