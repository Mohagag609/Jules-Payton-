from django.urls import path
from accounting.views import partners as views
from accounting.views.simple_views import simple_partners_list

app_name = 'partners'

urlpatterns = [
    path('', simple_partners_list, name='list'),  # Temporarily use simple view
    path('<int:pk>/update/', views.partner_update_view, name='update'),
    path('<int:pk>/get-form/', views.partner_get_form_view, name='get_form'),
    path('<int:pk>/delete/', views.partner_delete_view, name='delete'),
]
