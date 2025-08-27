from django.urls import path
from accounting.views import settlements as views

app_name = 'settlements'

urlpatterns = [
    path('', views.settlement_create_view, name='create'),
    path('<int:pk>/', views.settlement_detail_view, name='detail'),
    path('history/', views.settlement_list_view, name='list'),
]
