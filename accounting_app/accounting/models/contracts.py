from django.db import models
from django.core.validators import MinValueValidator
from .customers import Customer
from .units import Unit
from .groups import PartnersGroup

class Contract(models.Model):
    """
    يمثل عقد بيع وحدة لعميل، ويحدد شروط السداد.
    """
    class ScheduleType(models.TextChoices):
        MONTHLY = 'monthly', 'شهري'
        QUARTERLY = 'quarterly', 'ربع سنوي'
        YEARLY = 'yearly', 'سنوي'

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="رقم العقد"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name="العميل"
    )
    unit = models.OneToOneField( # Assuming a unit can only be sold once.
        Unit,
        on_delete=models.PROTECT,
        related_name='contract',
        verbose_name="الوحدة"
    )
    unit_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="قيمة الوحدة في العقد"
    )
    down_payment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="الدفعة المقدمة"
    )
    installments_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="عدد الأقساط"
    )
    schedule_type = models.CharField(
        max_length=20,
        choices=ScheduleType.choices,
        default=ScheduleType.MONTHLY,
        verbose_name="نوع جدولة الأقساط"
    )
    start_date = models.DateField(
        verbose_name="تاريخ بداية الأقساط"
    )
    partners_group = models.ForeignKey(
        PartnersGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="مجموعة الشركاء (اختياري)"
    )
    # Commission fields
    broker_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="اسم السمسار"
    )
    broker_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="نسبة العمولة %"
    )
    broker_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="مبلغ العمولة"
    )
    commission_safe = models.ForeignKey(
        'Safe',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contract_commissions',
        verbose_name="خزنة العمولة"
    )
    # Financial fields
    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="مبلغ الخصم"
    )
    maintenance_deposit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="وديعة الصيانة"
    )
    # Annual payment fields
    extra_annual = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="عدد الدفعات السنوية الإضافية"
    )
    annual_payment_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="قيمة الدفعة السنوية"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "عقد"
        verbose_name_plural = "العقود"
        ordering = ['-start_date']

    def __str__(self):
        return f"عقد {self.code} للعميل {self.customer.name}"

    @property
    def remaining_amount(self):
        return self.unit_value - self.down_payment
