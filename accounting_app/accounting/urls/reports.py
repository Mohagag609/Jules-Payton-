"""
Reports URLs
"""

from django.urls import path
from accounting.views.reports import (
    reports_home_view,
    financial_reports_view,
    partner_reports_view,
    unit_reports_view,
    overdue_report_view,
    cashflow_report_view,
    export_report_view,
)

urlpatterns = [
    path('', reports_home_view, name='reports'),
    path('financial/', financial_reports_view, name='financial_reports'),
    path('partners/', partner_reports_view, name='partner_reports'),
    path('units/', unit_reports_view, name='unit_reports'),
    path('overdue/', overdue_report_view, name='overdue_report'),
    path('cashflow/', cashflow_report_view, name='cashflow_report'),
    path('export/<str:report_type>/', export_report_view, name='export_report'),
]