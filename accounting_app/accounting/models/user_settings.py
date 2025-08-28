from django.db import models
from django.contrib.auth.models import User

class UserSettings(models.Model):
    """
    إعدادات المستخدم الشخصية للواجهة.
    """
    class Theme(models.TextChoices):
        LIGHT = 'light', 'فاتح'
        DARK = 'dark', 'داكن'
        AUTO = 'auto', 'تلقائي'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name="المستخدم"
    )
    theme = models.CharField(
        max_length=10,
        choices=Theme.choices,
        default=Theme.DARK,
        verbose_name="المظهر"
    )
    font_size = models.PositiveIntegerField(
        default=16,
        verbose_name="حجم الخط"
    )
    is_locked = models.BooleanField(
        default=False,
        verbose_name="التطبيق مقفل"
    )
    lock_password = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="كلمة مرور القفل"
    )
    # Preferences
    enable_shortcuts = models.BooleanField(
        default=True,
        verbose_name="تفعيل اختصارات لوحة المفاتيح"
    )
    enable_inline_editing = models.BooleanField(
        default=True,
        verbose_name="تفعيل التعديل المباشر"
    )
    enable_undo_redo = models.BooleanField(
        default=True,
        verbose_name="تفعيل التراجع/الإعادة"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخر تحديث"
    )

    class Meta:
        verbose_name = "إعدادات المستخدم"
        verbose_name_plural = "إعدادات المستخدمين"

    def __str__(self):
        return f"إعدادات {self.user.username}"