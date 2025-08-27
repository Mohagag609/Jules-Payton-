from django.urls import path
from accounting.views import partners as views

app_name = 'partners'

urlpatterns = [
    path('', views.partner_list_view, name='list'),
    path('create/', views.partner_create_view, name='create'),
    path('<int:pk>/edit/', views.partner_edit_view, name='edit'),
    path('<int:pk>/delete/', views.partner_delete_view, name='delete'),
]
