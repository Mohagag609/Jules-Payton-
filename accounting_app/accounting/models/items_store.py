from django.db import models
from .suppliers import Supplier

class Item(models.Model):
    """
    يمثل صنفاً في المخزن (مواد بناء، أدوات، الخ).
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="كود الصنف"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="اسم الصنف"
    )
    uom = models.CharField(
        max_length=50,
        verbose_name="وحدة القياس" # (Unit of Measurement)
    )
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="سعر الوحدة"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="المورد الافتراضي"
    )

    class Meta:
        verbose_name = "صنف مخزن"
        verbose_name_plural = "أصناف المخزن"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_stock_balance(self):
        """
        يحسب الرصيد الحالي للصنف من حركات المخزن.
        """
        in_qty = self.stock_moves.filter(direction='IN').aggregate(total=models.Sum('qty'))['total'] or 0
        out_qty = self.stock_moves.filter(direction='OUT').aggregate(total=models.Sum('qty'))['total'] or 0
        return in_qty - out_qty
