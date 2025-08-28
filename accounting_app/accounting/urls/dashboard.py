"""
Dashboard URLs
"""

from django.urls import path
from accounting.views.dashboard import (
    dashboard_view,
    dashboard_export_view,
    dashboard_print_view,
)

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('export/', dashboard_export_view, name='dashboard_export'),
    path('print/', dashboard_print_view, name='dashboard_print'),
]