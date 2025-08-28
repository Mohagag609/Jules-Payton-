from django.apps import AppConfig


class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounting'
    verbose_name = 'المحاسبة'
    from django.apps import AppConfig
from django.db.models.signals import post_migrate

def _ensure_superuser(sender, **kwargs):
    # ينفّذ بعد المايجريشن
    import os
    from django.contrib.auth import get_user_model
    User = get_user_model()
    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
    email    = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "ChangeMe!123")

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)

class AccountingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounting"

    def ready(self):
        # اربط السيجنال بحيث يتنفّذ بعد migrate
        post_migrate.connect(_ensure_superuser, sender=self)
