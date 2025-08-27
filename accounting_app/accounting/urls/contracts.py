from django.urls import path
from accounting.views import contracts as views

app_name = 'contracts'

urlpatterns = [
    path('', views.contract_list_view, name='list'),
    path('create/', views.contract_create_view, name='create'),
    # The wizard will be handled by the create_view, maybe with steps in query params
    # Or we can have separate URLs if the logic is complex.
    # For now, one URL is enough.
    path('<int:pk>/', views.contract_detail_view, name='detail'),
]
