from django.urls import path
from accounting.views import safes as views

app_name = 'safes'

urlpatterns = [
    path('', views.safe_list_view, name='list'),
    path('<int:pk>/update/', views.safe_update_view, name='update'),
    path('<int:pk>/get-form/', views.safe_get_form_view, name='get_form'),
    path('<int:pk>/delete/', views.safe_delete_view, name='delete'),
]
