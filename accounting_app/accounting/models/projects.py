from django.db import models

class Project(models.Model):
    """
    يمثل مشروع مقاولات أو صيانة.
    """
    class ProjectType(models.TextChoices):
        BUILD = 'build', 'بناء'
        MAINTENANCE = 'maintenance', 'صيانة'
        RENOVATION = 'renovation', 'ترميم'

    class ProjectStatus(models.TextChoices):
        ONGOING = 'ongoing', 'قيد التنفيذ'
        DONE = 'done', 'منتهي'
        HOLD = 'hold', 'متوقف'

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="كود المشروع"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="اسم المشروع"
    )
    type = models.CharField(
        max_length=20,
        choices=ProjectType.choices,
        verbose_name="نوع المشروع"
    )
    start_date = models.DateField(
        verbose_name="تاريخ البدء"
    )
    end_date = models.DateField(
        null=True, blank=True,
        verbose_name="تاريخ الانتهاء"
    )
    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.ONGOING,
        verbose_name="حالة المشروع"
    )
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="الميزانية التقديرية"
    )

    class Meta:
        verbose_name = "مشروع"
        verbose_name_plural = "المشاريع"
        ordering = ['-start_date']

    def __str__(self):
        return self.name
