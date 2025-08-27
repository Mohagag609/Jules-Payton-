from django.urls import path
from accounting.views import safes as views

app_name = 'safes'

urlpatterns = [
    path('', views.safe_list_view, name='list'),
    path('create/', views.safe_create_view, name='create'),
    path('<int:pk>/edit/', views.safe_edit_view, name='edit'),
    path('<int:pk>/delete/', views.safe_delete_view, name='delete'),
]
