from django.db import models
from django.core.exceptions import ValidationError
from .partners import Partner

class Safe(models.Model):
    """
    يمثل خزنة أو محفظة نقدية، سواء كانت عامة أو خاصة بشريك.
    """
    name = models.CharField(
        max_length=255,
        verbose_name="اسم الخزنة/المحفظة"
    )
    is_partner_wallet = models.BooleanField(
        default=False,
        verbose_name="هل هي محفظة شريك؟"
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="الشريك (إذا كانت محفظة)"
    )

    class Meta:
        verbose_name = "خزنة/محفظة"
        verbose_name_plural = "الخزائن والمحافظ"
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        """
        يفرض قاعدة أن المحفظة المرتبطة بشريك يجب أن يكون حقل الشريك فيها محدداً.
        """
        super().clean()
        if self.is_partner_wallet and self.partner is None:
            raise ValidationError({
                'partner': "يجب تحديد شريك عندما تكون هذه محفظة شريك."
            })
        if not self.is_partner_wallet and self.partner is not None:
            raise ValidationError({
                'partner': "لا يمكن تحديد شريك إلا إذا كانت محفظة شريك."
            })
