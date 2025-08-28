from django.urls import path
from accounting.views import customers as views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list_view, name='list'),
    path('<int:pk>/update/', views.customer_update_view, name='update'),
    path('<int:pk>/get-form/', views.customer_get_form_view, name='get_form'),
    path('<int:pk>/delete/', views.customer_delete_view, name='delete'),
]
