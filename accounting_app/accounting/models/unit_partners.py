from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum

class UnitPartner(models.Model):
    """
    يمثل ربط الشركاء بالوحدات مع نسب الملكية.
    """
    unit = models.ForeignKey(
        'Unit',
        on_delete=models.CASCADE,
        related_name='unit_partners',
        verbose_name="الوحدة"
    )
    partner = models.ForeignKey(
        'Partner',
        on_delete=models.CASCADE,
        related_name='unit_partnerships',
        verbose_name="الشريك"
    )
    percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="نسبة الملكية %"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "شريك وحدة"
        verbose_name_plural = "شركاء الوحدات"
        unique_together = ('unit', 'partner')
        ordering = ['unit', '-percent']

    def __str__(self):
        return f"{self.partner.name} - {self.unit.name} ({self.percent}%)"

    def clean(self):
        """
        التحقق من أن إجمالي النسب للوحدة لا يتجاوز 100%.
        """
        total_percent = UnitPartner.objects.filter(
            unit=self.unit
        ).exclude(
            pk=self.pk
        ).aggregate(
            total=Sum('percent')
        )['total'] or 0

        if total_percent + self.percent > 100:
            raise ValidationError(
                f"إجمالي النسب للوحدة يتجاوز 100%. "
                f"النسبة الحالية: {total_percent}%, "
                f"النسبة المضافة: {self.percent}%"
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)