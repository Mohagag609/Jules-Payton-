from django.db import models

class Supplier(models.Model):
    """
    يمثل المورد الذي تتعامل معه الشركة.
    """
    name = models.CharField(
        max_length=255,
        verbose_name="اسم المورد"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="رقم الهاتف"
    )

    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردون"
        ordering = ['name']

    def __str__(self):
        return self.name
