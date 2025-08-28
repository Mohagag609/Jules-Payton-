from django.urls import path
from accounting.views import customers as views
from accounting.views.simple_views import simple_customers_list

app_name = 'customers'

urlpatterns = [
    path('', simple_customers_list, name='list'),  # Temporarily use simple view
    path('<int:pk>/update/', views.customer_update_view, name='update'),
    path('<int:pk>/get-form/', views.customer_get_form_view, name='get_form'),
    path('<int:pk>/delete/', views.customer_delete_view, name='delete'),
]
