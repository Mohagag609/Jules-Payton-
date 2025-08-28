"""
Units URLs
"""

from django.urls import path
from accounting.views import units as views

app_name = 'units'

urlpatterns = [
    path('', views.unit_list_view, name='unit_list'),
    path('create/', views.unit_create_view, name='unit_create'),
    path('<int:pk>/', views.unit_detail_view, name='unit_detail'),
    path('<int:pk>/edit/', views.unit_edit_view, name='unit_edit'),
    path('<int:pk>/delete/', views.unit_delete_view, name='unit_delete'),
    path('<int:pk>/add-partner/', views.unit_add_partner, name='unit_add_partner'),
    path('<int:pk>/inline-edit/', views.unit_inline_edit, name='unit_inline_edit'),
    path('<int:pk>/return/preview/', views.unit_return_preview, name='unit_return_preview'),
    path('<int:pk>/return/execute/', views.unit_return_execute, name='unit_return_execute'),
]