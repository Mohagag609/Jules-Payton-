from django.db import models
from django.utils import timezone
from .items_store import Item
from .projects import Project

class StockMove(models.Model):
    """
    يمثل حركة مخزنية (إدخال أو إخراج) لصنف معين.
    """
    class MoveDirection(models.TextChoices):
        IN = 'IN', 'إدخال (توريد)'
        OUT = 'OUT', 'إخراج (صرف)'

    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name='stock_moves',
        verbose_name="الصنف"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='stock_moves',
        verbose_name="المشروع (في حالة الصرف)"
    )
    qty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="الكمية"
    )
    direction = models.CharField(
        max_length=3,
        choices=MoveDirection.choices,
        verbose_name="اتجاه الحركة"
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name="تاريخ الحركة"
    )
    notes = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="ملاحظات"
    )

    class Meta:
        verbose_name = "حركة مخزن"
        verbose_name_plural = "حركات المخزن"
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_direction_display()} لكمية {self.qty} من {self.item.name}"
