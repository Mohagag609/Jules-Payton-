from django.urls import path
from accounting.views import safes as views
from accounting.views.simple_fixed import simple_safes_list

app_name = 'safes'

urlpatterns = [
    path('', simple_safes_list, name='list'),  # Temporarily use simple view
    path('<int:pk>/update/', views.safe_update_view, name='update'),
    path('<int:pk>/get-form/', views.safe_get_form_view, name='get_form'),
    path('<int:pk>/delete/', views.safe_delete_view, name='delete'),
]
