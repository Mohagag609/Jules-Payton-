from django.db import models
from django.core.exceptions import ValidationError

class Transfer(models.Model):
    """
    يمثل عملية تحويل مالية بين خزنتين.
    """
    from_safe = models.ForeignKey(
        'Safe',
        on_delete=models.PROTECT,
        related_name='transfers_out',
        verbose_name="من خزنة"
    )
    to_safe = models.ForeignKey(
        'Safe',
        on_delete=models.PROTECT,
        related_name='transfers_in',
        verbose_name="إلى خزنة"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="المبلغ"
    )
    date = models.DateField(
        verbose_name="تاريخ التحويل"
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
        verbose_name = "تحويل"
        verbose_name_plural = "التحويلات"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"تحويل {self.amount} من {self.from_safe.name} إلى {self.to_safe.name}"

    def clean(self):
        """
        التحقق من صحة التحويل.
        """
        if self.from_safe == self.to_safe:
            raise ValidationError("لا يمكن التحويل من وإلى نفس الخزنة.")
        
        if self.from_safe.balance < self.amount:
            raise ValidationError(
                f"رصيد الخزنة '{self.from_safe.name}' غير كافٍ. "
                f"الرصيد الحالي: {self.from_safe.balance}"
            )

    def save(self, *args, **kwargs):
        """
        حفظ التحويل وتحديث أرصدة الخزن.
        """
        is_new = self.pk is None
        
        if is_new:
            self.clean()
            # خصم من الخزنة المصدر
            self.from_safe.balance -= self.amount
            self.from_safe.save()
            
            # إضافة إلى الخزنة الهدف
            self.to_safe.balance += self.amount
            self.to_safe.save()
        
        super().save(*args, **kwargs)