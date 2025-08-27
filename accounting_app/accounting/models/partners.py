from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Partner(models.Model):
    """
    يمثل الشريك في الشركة.
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="كود الشريك"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="اسم الشريك"
    )
    share_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="نسبة الحصة (٪)"
    )
    opening_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.0,
        verbose_name="الرصيد الافتتاحي"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="ملاحظات"
    )

    class Meta:
        verbose_name = "شريك"
        verbose_name_plural = "الشركاء"
        ordering = ['name']

    def __str__(self):
        return self.name
