from django.urls import path
from accounting.views import partners as views

app_name = 'partners'

urlpatterns = [
    path('', views.partner_list_view, name='list'),
    path('<int:pk>/update/', views.partner_update_view, name='update'),
    path('<int:pk>/get-form/', views.partner_get_form_view, name='get_form'),
    path('<int:pk>/delete/', views.partner_delete_view, name='delete'),
]
