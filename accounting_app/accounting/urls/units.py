from django.urls import path
from accounting.views import units as views

app_name = 'units'

urlpatterns = [
    path('', views.unit_list_view, name='list'),
    path('<int:pk>/update/', views.unit_update_view, name='update'),
    path('<int:pk>/get-form/', views.unit_get_form_view, name='get_form'),
    path('<int:pk>/delete/', views.unit_delete_view, name='delete'),
]
