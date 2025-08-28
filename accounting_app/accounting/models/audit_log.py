from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class AuditLog(models.Model):
    """
    سجل تتبع لجميع التغييرات في النظام.
    """
    class Action(models.TextChoices):
        CREATE = 'create', 'إنشاء'
        UPDATE = 'update', 'تحديث'
        DELETE = 'delete', 'حذف'
        OTHER = 'other', 'أخرى'

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="المستخدم"
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        verbose_name="الإجراء"
    )
    description = models.CharField(
        max_length=500,
        verbose_name="الوصف"
    )
    # Generic relation to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # JSON field for additional details
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="تفاصيل إضافية"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="عنوان IP"
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="المتصفح"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="الوقت والتاريخ"
    )

    class Meta:
        verbose_name = "سجل تتبع"
        verbose_name_plural = "سجلات التتبع"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.action} - {self.description} - {self.timestamp}"