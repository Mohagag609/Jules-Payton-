"""
Partner Debts URLs
"""

from django.urls import path
from accounting.views import partner_debts as views

app_name = 'partner_debts'

urlpatterns = [
    path('', views.debt_list, name='debt_list'),
    path('<int:pk>/pay/', views.debt_pay, name='debt_pay'),
]