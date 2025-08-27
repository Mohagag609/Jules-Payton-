from django.urls import path
from accounting.views import reports as views

app_name = 'reports'

urlpatterns = [
    path('', views.report_index_view, name='index'),
    path('treasury/', views.treasury_report_view, name='treasury'),
    path('installments/', views.installments_report_view, name='installments'),
    path('partner-balances/', views.partner_balances_report_view, name='partner_balances'),
    path('expenses/', views.expenses_report_view, name='expenses'),
]
