from django.urls import path
from accounting.views import contracts as views
from accounting.views.simple_fixed import simple_contracts_list

app_name = 'contracts'

urlpatterns = [
    path('', simple_contracts_list, name='list'),  # Temporarily use simple view
    path('create/', views.contract_create_view, name='create'),
    # The wizard will be handled by the create_view, maybe with steps in query params
    # Or we can have separate URLs if the logic is complex.
    # For now, one URL is enough.
    path('<int:pk>/', views.contract_detail_view, name='detail'),
]
