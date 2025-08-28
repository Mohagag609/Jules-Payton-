# Generated manually for new models

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_add_all_missing_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create Broker model
        migrations.CreateModel(
            name='Broker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='اسم السمسار')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='رقم الهاتف')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
            ],
            options={
                'verbose_name': 'سمسار',
                'verbose_name_plural': 'السماسرة',
            },
        ),
        
        # Create BrokerDue model
        migrations.CreateModel(
            name='BrokerDue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('broker_name', models.CharField(max_length=255, verbose_name='اسم السمسار')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='المبلغ')),
                ('due_date', models.DateField(verbose_name='تاريخ الاستحقاق')),
                ('payment_date', models.DateField(blank=True, null=True, verbose_name='تاريخ الدفع')),
                ('status', models.CharField(choices=[('due', 'مستحق'), ('paid', 'مدفوع')], default='due', max_length=10, verbose_name='الحالة')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='broker_dues', to='accounting.contract', verbose_name='العقد')),
            ],
            options={
                'verbose_name': 'مستحقات السمسار',
                'verbose_name_plural': 'مستحقات السماسرة',
                'ordering': ['-due_date'],
            },
        ),
        
        # Create UnitPartner model
        migrations.CreateModel(
            name='UnitPartner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='نسبة الملكية %')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_partnerships', to='accounting.partner', verbose_name='الشريك')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_partners', to='accounting.unit', verbose_name='الوحدة')),
            ],
            options={
                'verbose_name': 'ملكية الوحدة',
                'verbose_name_plural': 'ملكيات الوحدات',
                'unique_together': {('unit', 'partner')},
            },
        ),
        
        # Create Transfer model
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='المبلغ')),
                ('date', models.DateField(verbose_name='التاريخ')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('from_safe', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transfers_out', to='accounting.safe', verbose_name='من خزنة')),
                ('to_safe', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transfers_in', to='accounting.safe', verbose_name='إلى خزنة')),
            ],
            options={
                'verbose_name': 'تحويل',
                'verbose_name_plural': 'التحويلات',
                'ordering': ['-date'],
            },
        ),
        
        # Create PartnerDebt model
        migrations.CreateModel(
            name='PartnerDebt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='المبلغ')),
                ('due_date', models.DateField(verbose_name='تاريخ الاستحقاق')),
                ('payment_date', models.DateField(blank=True, null=True, verbose_name='تاريخ السداد')),
                ('status', models.CharField(choices=[('pending', 'معلق'), ('paid', 'مدفوع')], default='pending', max_length=10, verbose_name='الحالة')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('owed_partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debts_to_receive', to='accounting.partner', verbose_name='الشريك الدائن')),
                ('paying_partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debts_to_pay', to='accounting.partner', verbose_name='الشريك المدين')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partner_debts', to='accounting.unit', verbose_name='الوحدة')),
            ],
            options={
                'verbose_name': 'دين شريك',
                'verbose_name_plural': 'ديون الشركاء',
                'ordering': ['-due_date'],
            },
        ),
        
        # Create UserSettings model
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(choices=[('light', 'فاتح'), ('dark', 'داكن')], default='light', max_length=10, verbose_name='السمة')),
                ('font_size', models.CharField(choices=[('small', 'صغير'), ('medium', 'متوسط'), ('large', 'كبير')], default='medium', max_length=10, verbose_name='حجم الخط')),
                ('is_locked', models.BooleanField(default=False, verbose_name='التطبيق مقفل')),
                ('enable_inline_edit', models.BooleanField(default=True, verbose_name='تفعيل التعديل المباشر')),
                ('enable_keyboard_shortcuts', models.BooleanField(default=True, verbose_name='تفعيل اختصارات لوحة المفاتيح')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'إعدادات المستخدم',
                'verbose_name_plural': 'إعدادات المستخدمين',
            },
        ),
        
        # Create AuditLog model
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', 'إنشاء'), ('update', 'تحديث'), ('delete', 'حذف'), ('view', 'عرض')], max_length=10, verbose_name='الإجراء')),
                ('model_name', models.CharField(max_length=50, verbose_name='النموذج')),
                ('object_id', models.CharField(max_length=50, verbose_name='معرف الكائن')),
                ('object_repr', models.CharField(max_length=255, verbose_name='تمثيل الكائن')),
                ('changes', models.JSONField(blank=True, null=True, verbose_name='التغييرات')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='الوقت')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='عنوان IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='وكيل المستخدم')),
                ('description', models.TextField(blank=True, verbose_name='الوصف')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'سجل التتبع',
                'verbose_name_plural': 'سجلات التتبع',
                'ordering': ['-timestamp'],
            },
        ),
    ]