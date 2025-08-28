"""
Transfers URLs
"""

from django.urls import path
from accounting.views import transfers as views

app_name = 'transfers'

urlpatterns = [
    path('', views.transfer_list, name='transfer_list'),
    path('create/', views.transfer_create, name='transfer_create'),
    path('<int:pk>/', views.transfer_detail, name='transfer_detail'),
]