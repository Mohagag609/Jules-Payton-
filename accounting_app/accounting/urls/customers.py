from django.urls import path
from accounting.views import customers as views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list_view, name='list'),
    path('create/', views.customer_create_view, name='create'),
    path('<int:pk>/edit/', views.customer_edit_view, name='edit'),
    path('<int:pk>/delete/', views.customer_delete_view, name='delete'),
]
