from django.db import models

class Broker(models.Model):
    """
    يمثل السمسار الذي يجلب العملاء ويحصل على عمولات.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="اسم السمسار"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="رقم الهاتف"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="ملاحظات"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "سمسار"
        verbose_name_plural = "السماسرة"
        ordering = ['name']

    def __str__(self):
        return self.name


class BrokerDue(models.Model):
    """
    يمثل العمولة المستحقة للسمسار على عقد معين.
    """
    class Status(models.TextChoices):
        DUE = 'due', 'مستحقة'
        PAID = 'paid', 'مدفوعة'
        CANCELLED = 'cancelled', 'ملغاة'

    contract = models.ForeignKey(
        'Contract',
        on_delete=models.CASCADE,
        related_name='broker_dues',
        verbose_name="العقد"
    )
    broker_name = models.CharField(
        max_length=255,
        verbose_name="اسم السمسار"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="مبلغ العمولة"
    )
    due_date = models.DateField(
        verbose_name="تاريخ الاستحقاق"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DUE,
        verbose_name="الحالة"
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاريخ الدفع"
    )
    paid_from_safe = models.ForeignKey(
        'Safe',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='broker_payments',
        verbose_name="خزنة الدفع"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "عمولة مستحقة"
        verbose_name_plural = "العمولات المستحقة"
        ordering = ['-due_date']

    def __str__(self):
        return f"عمولة {self.broker_name} - {self.amount}"