from django.urls import path, include
from accounting.views import dashboard

app_name = 'accounting'

urlpatterns = [
    path('', dashboard.dashboard_view, name='dashboard'),
    path('partners/', include('accounting.urls.partners', namespace='partners')),
    path('safes/', include('accounting.urls.safes', namespace='safes')),
    path('customers/', include('accounting.urls.customers', namespace='customers')),
    path('suppliers/', include('accounting.urls.suppliers', namespace='suppliers')),
    path('units/', include('accounting.urls.units', namespace='units')),
    path('projects/', include('accounting.urls.projects_store', namespace='projects_store')),
    path('contracts/', include('accounting.urls.contracts', namespace='contracts')),
    path('installments/', include('accounting.urls.installments', namespace='installments')),
    path('vouchers/', include('accounting.urls.vouchers', namespace='vouchers')),
    path('reports/', include('accounting.urls.reports', namespace='reports')),
    path('settlements/', include('accounting.urls.settlements', namespace='settlements')),
    # Add other app-specific url modules here
]
