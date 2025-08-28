"""
Backup URLs
"""

from django.urls import path
from accounting.views import backup as views

app_name = 'backup'

urlpatterns = [
    path('', views.backup_dashboard, name='backup_dashboard'),
    path('export/', views.backup_export, name='backup_export'),
    path('restore/', views.backup_restore, name='backup_restore'),
]