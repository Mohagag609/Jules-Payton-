from django.urls import path
from accounting.views import units as views

app_name = 'units'

urlpatterns = [
    path('', views.unit_list_view, name='list'),
    path('create/', views.unit_create_view, name='create'),
    path('<int:pk>/edit/', views.unit_edit_view, name='edit'),
    path('<int:pk>/delete/', views.unit_delete_view, name='delete'),
]
