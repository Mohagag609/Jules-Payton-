from django.urls import path
from accounting.views import suppliers as views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list_view, name='list'),
    path('create/', views.supplier_create_view, name='create'),
    path('<int:pk>/edit/', views.supplier_edit_view, name='edit'),
    path('<int:pk>/delete/', views.supplier_delete_view, name='delete'),
]
