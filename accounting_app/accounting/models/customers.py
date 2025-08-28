from django.db import models

class Customer(models.Model):
    """
    يمثل العميل الذي يتعامل مع الشركة.
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="كود العميل"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="اسم العميل"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="رقم الهاتف"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="البريد الإلكتروني"
    )
    address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="العنوان"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="نشط"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"
        ordering = ['name']

    def __str__(self):
        return self.name
