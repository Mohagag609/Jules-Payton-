from django.db import models
from .projects import Project

class Settlement(models.Model):
    """
    يمثل تسوية بين الشركاء لفترة معينة، سواء لمشروع أو بشكل عام.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="المشروع المرتبط (اختياري)"
    )
    period_from = models.DateField(
        verbose_name="من تاريخ"
    )
    period_to = models.DateField(
        verbose_name="إلى تاريخ"
    )
    pre_balances = models.JSONField(
        default=dict,
        verbose_name="الأرصدة قبل التسوية"
    )
    post_balances = models.JSONField(
        default=dict,
        verbose_name="الأرصدة بعد التسوية"
    )
    details = models.JSONField(
        default=dict,
        help_text="تحتوي على التحويلات المطلوبة بين الشركاء لتسوية الحسابات.",
        verbose_name="تفاصيل التسوية"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "تسوية شركاء"
        verbose_name_plural = "تسويات الشركاء"
        ordering = ['-period_to']

    def __str__(self):
        if self.project:
            return f"تسوية مشروع {self.project.name} للفترة من {self.period_from} إلى {self.period_to}"
        return f"تسوية عامة للفترة من {self.period_from} إلى {self.period_to}"
