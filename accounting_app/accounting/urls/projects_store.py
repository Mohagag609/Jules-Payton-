from django.urls import path
from accounting.views import projects_store as views

app_name = 'projects_store'

urlpatterns = [
    # Project URLs
    path('', views.project_list_view, name='project_list'),
    path('create/', views.project_create_view, name='project_create'),
    path('<int:pk>/edit/', views.project_edit_view, name='project_edit'),
    path('<int:pk>/delete/', views.project_delete_view, name='project_delete'),

    # Item URLs
    path('store/items/', views.item_list_view, name='item_list'),
    path('store/items/create/', views.item_create_view, name='item_create'),
    path('store/items/<int:pk>/edit/', views.item_edit_view, name='item_edit'),
    path('store/items/<int:pk>/delete/', views.item_delete_view, name='item_delete'),

    # Stock Move URLs
    path('store/moves/', views.stock_move_list_view, name='move_list'),
    path('store/moves/create/', views.stock_move_create_view, name='move_create'),
]
