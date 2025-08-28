from django.urls import path
from accounting.views import projects_store as views

app_name = 'projects_store'

urlpatterns = [
    # Project URLs
    path('', views.project_list_view, name='project_list'),
    path('<int:pk>/update/', views.project_update_view, name='project_update'),
    path('<int:pk>/get-form/', views.project_get_form_view, name='project_get_form'),
    path('<int:pk>/delete/', views.project_delete_view, name='project_delete'),

    # Item URLs
    path('store/items/', views.item_list_view, name='item_list'),
    path('store/items/<int:pk>/update/', views.item_update_view, name='item_update'),
    path('store/items/<int:pk>/get-form/', views.item_get_form_view, name='item_get_form'),
    path('store/items/<int:pk>/delete/', views.item_delete_view, name='item_delete'),

    # Stock Move URLs
    path('store/moves/', views.stock_move_list_view, name='move_list'),
]
