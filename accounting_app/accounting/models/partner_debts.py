from django.db import models

class PartnerDebt(models.Model):
    """
    يمثل دين بين شريكين نتيجة عملية إرجاع وحدة.
    """
    class Status(models.TextChoices):
        UNPAID = 'unpaid', 'غير مدفوع'
        PAID = 'paid', 'مدفوع'
        CANCELLED = 'cancelled', 'ملغي'

    unit = models.ForeignKey(
        'Unit',
        on_delete=models.CASCADE,
        related_name='partner_debts',
        verbose_name="الوحدة"
    )
    paying_partner = models.ForeignKey(
        'Partner',
        on_delete=models.CASCADE,
        related_name='debts_to_pay',
        verbose_name="الشريك الدافع"
    )
    owed_partner = models.ForeignKey(
        'Partner',
        on_delete=models.CASCADE,
        related_name='debts_to_receive',
        verbose_name="الشريك المستحق"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="المبلغ"
    )
    due_date = models.DateField(
        verbose_name="تاريخ الاستحقاق"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNPAID,
        verbose_name="الحالة"
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاريخ السداد"
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
        verbose_name = "دين شريك"
        verbose_name_plural = "ديون الشركاء"
        ordering = ['-due_date', '-created_at']

    def __str__(self):
        return f"دين {self.amount} من {self.paying_partner.name} إلى {self.owed_partner.name}"