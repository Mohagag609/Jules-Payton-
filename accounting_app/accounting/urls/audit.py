"""
Audit Log URLs
"""

from django.urls import path
from accounting.views import audit as views

app_name = 'audit'

urlpatterns = [
    path('', views.audit_log_list, name='audit_log_list'),
    path('export/', views.audit_log_export, name='audit_log_export'),
]