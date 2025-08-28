"""
Management command to create a superuser automatically
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser if none exists'

    def handle(self, *args, **options):
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123456'
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created superuser: admin')
            )
            self.stdout.write(
                self.style.WARNING('Password: admin123456 (Please change it!)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Superuser already exists')
            )