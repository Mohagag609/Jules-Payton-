from decimal import Decimal
from django.db import models
from django.utils import timezone
from .contracts import Contract

class Installment(models.Model):
    """
    يمثل قسطاً واحداً من جدول أقساط العقد.
    """
    class InstallmentStatus(models.TextChoices):
        PENDING = 'PENDING', 'قيد الانتظار'
        PAID = 'PAID', 'مدفوع'
        LATE = 'LATE', 'متأخر'

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='installments',
        verbose_name="العقد"
    )
    seq_no = models.PositiveIntegerField(
        verbose_name="رقم القسط"
    )
    due_date = models.DateField(
        verbose_name="تاريخ الاستحقاق"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="قيمة القسط"
    )
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.0'),
        verbose_name="المبلغ المدفوع"
    )
    status = models.CharField(
        max_length=10,
        choices=InstallmentStatus.choices,
        default=InstallmentStatus.PENDING,
        verbose_name="حالة القسط"
    )

    class Meta:
        verbose_name = "قسط"
        verbose_name_plural = "الأقساط"
        unique_together = ('contract', 'seq_no')
        ordering = ['contract', 'seq_no']

    def __str__(self):
        return f"القسط رقم {self.seq_no} للعقد {self.contract.code}"

    def update_status(self):
        """
        تحديث حالة القسط بناءً على المبلغ المدفوع وتاريخ الاستحقاق.
        """
        if self.paid_amount >= self.amount:
            self.status = self.InstallmentStatus.PAID
        elif timezone.now().date() > self.due_date:
            self.status = self.InstallmentStatus.LATE
        else:
            self.status = self.InstallmentStatus.PENDING
        self.save()

    @property
    def is_paid(self):
        return self.status == self.InstallmentStatus.PAID

    @property
    def remaining_to_pay(self):
        return self.amount - self.paid_amount
