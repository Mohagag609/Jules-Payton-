"""
Treasury URLs
"""

from django.urls import path
from accounting.views import treasury as views

app_name = 'treasury'

urlpatterns = [
    path('', views.treasury_dashboard, name='treasury_dashboard'),
    path('safes/', views.safe_list, name='safe_list'),
    path('transfers/', views.transfer_list, name='transfer_list'),
]