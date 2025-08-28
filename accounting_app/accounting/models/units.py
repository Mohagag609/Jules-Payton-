from django.db import models
from .groups import PartnersGroup

class Unit(models.Model):
    """
    يمثل وحدة سكنية أو تجارية أو غيرها.
    """
    class UnitType(models.TextChoices):
        RESIDENTIAL = 'residential', 'سكني'
        COMMERCIAL = 'commercial', 'تجاري'
        SCHOOL = 'school', 'مدرسة'
        ADMINISTRATIVE = 'administrative', 'إداري'
        MEDICAL = 'medical', 'طبي'
        INDUSTRIAL = 'industrial', 'صناعي'
        OTHER = 'other', 'أخرى'

    class UnitGroup(models.TextChoices):
        RESIDENTIAL = 'res', 'سكني'
        COMMERCIAL = 'com', 'تجاري'

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="كود الوحدة"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="اسم/وصف الوحدة"
    )
    building_no = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="رقم المبنى/العمارة"
    )
    floor = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="رقم الدور"
    )
    area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="المساحة (م²)"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'متاحة'),
            ('sold', 'مباعة'),
            ('reserved', 'محجوزة'),
            ('returned', 'مرتجعة'),
        ],
        default='available',
        verbose_name="الحالة"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="ملاحظات"
    )
    type = models.CharField(
        max_length=20,
        choices=UnitType.choices,
        default=UnitType.RESIDENTIAL,
        verbose_name="نوع الوحدة"
    )
    price_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="السعر الإجمالي للوحدة"
    )
    # The prompt seems to have a typo "group(res|com)". I am interpreting this as a grouping for the unit itself, not partner groups.
    # If this was meant to be a relation to PartnersGroup, the schema would be different.
    # I will name it `category` to avoid confusion with `PartnersGroup`.
    category = models.CharField(
        max_length=10,
        choices=UnitGroup.choices,
        verbose_name="تصنيف الوحدة"
    )
    # The prompt also mentions an optional link to a partner group.
    partners_group = models.ForeignKey(
        PartnersGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="مجموعة الشركاء المالكة"
    )

    class Meta:
        verbose_name = "وحدة"
        verbose_name_plural = "الوحدات"
        ordering = ['code']

    def __str__(self):
        return self.name
