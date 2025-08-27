from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from .partners import Partner

class PartnersGroup(models.Model):
    """
    مجموعة من الشركاء، تستخدم لربط العقود والوحدات بمجموعة معينة.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="اسم المجموعة"
    )

    class Meta:
        verbose_name = "مجموعة شركاء"
        verbose_name_plural = "مجموعات الشركاء"

    def __str__(self):
        return self.name

    def clean(self):
        """
        يضمن أن مجموع نسب أعضاء المجموعة يساوي 100%.
        يتم استدعاء هذا في نماذج Django (Forms) وفي لوحة التحكم.
        """
        super().clean()
        if self.pk: # Only validate for existing groups that have members
            total_percent = self.members.aggregate(total=models.Sum('percent'))['total'] or 0
            if total_percent != 100:
                raise ValidationError(
                    f"مجموع نسب أعضاء المجموعة يجب أن يكون 100%. المجموع الحالي هو {total_percent}%."
                )

class PartnersGroupMember(models.Model):
    """
    عضو في مجموعة شركاء بنسبة محددة.
    """
    group = models.ForeignKey(
        PartnersGroup,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name="المجموعة"
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.PROTECT,
        related_name='group_memberships',
        verbose_name="الشريك"
    )
    percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="النسبة في المجموعة (٪)"
    )

    class Meta:
        verbose_name = "عضو مجموعة"
        verbose_name_plural = "أعضاء المجموعات"
        unique_together = ('group', 'partner') # لا يمكن إضافة نفس الشريك مرتين لنفس المجموعة
        ordering = ['group', '-percent']

    def __str__(self):
        return f"{self.partner.name} في {self.group.name} ({self.percent}%)"
