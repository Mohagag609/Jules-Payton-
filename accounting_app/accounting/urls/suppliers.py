from django.urls import path
from accounting.views import suppliers as views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list_view, name='list'),
    path('<int:pk>/update/', views.supplier_update_view, name='update'),
    path('<int:pk>/get-form/', views.supplier_get_form_view, name='get_form'),
    path('<int:pk>/delete/', views.supplier_delete_view, name='delete'),
]
