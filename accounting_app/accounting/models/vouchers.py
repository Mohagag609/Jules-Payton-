from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

# Forward-declare models to handle circular dependencies if any
# Although in this structure, it's mostly one-way.
Safe = 'accounting.Safe'
Customer = 'accounting.Customer'
Partner = 'accounting.Partner'
Contract = 'accounting.Contract'
Installment = 'accounting.Installment'
Supplier = 'accounting.Supplier'
Project = 'accounting.Project'


class VoucherBase(models.Model):
    """
    نموذج أساسي مجرد للسندات (قبض وصرف).
    """
    date = models.DateField(
        default=timezone.now,
        verbose_name="تاريخ السند"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="المبلغ"
    )
    safe = models.ForeignKey(
        Safe,
        on_delete=models.PROTECT,
        verbose_name="الخزنة/المحفظة"
    )
    description = models.TextField(
        verbose_name="البيان/الوصف"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        abstract = True
        ordering = ['-date']


class ReceiptVoucher(VoucherBase):
    """
    سند قبض.
    """
    # Using string relations to avoid circular import errors
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="العميل"
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="الشريك"
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="العقد"
    )
    installment = models.ForeignKey(
        Installment,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='receipts',
        verbose_name="القسط"
    )

    class Meta:
        verbose_name = "سند قبض"
        verbose_name_plural = "سندات القبض"

    def __str__(self):
        return f"سند قبض رقم {self.pk} بمبلغ {self.amount}"


class PaymentVoucher(VoucherBase):
    """
    سند صرف.
    """
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="المورد"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="المشروع"
    )
    expense_head = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="بند المصروف"
    )

    class Meta:
        verbose_name = "سند صرف"
        verbose_name_plural = "سندات الصرف"

    def __str__(self):
        return f"سند صرف رقم {self.pk} بمبلغ {self.amount}"
