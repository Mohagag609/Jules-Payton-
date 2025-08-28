from django.urls import path, include
from accounting.views.dashboard import (
    undo_action, redo_action, update_theme, 
    global_search, lock_app, unlock_app
)
from accounting.views.test_dashboard import simple_dashboard_view, test_dashboard_data

app_name = 'accounting'

urlpatterns = [
    # Test URLs (temporary)
    path('test/', simple_dashboard_view, name='test_dashboard'),
    path('test/data/', test_dashboard_data, name='test_data'),
    
    # Dashboard
    path('', include('accounting.urls.dashboard')),
    
    # Core Modules
    path('partners/', include('accounting.urls.partners')),
    path('safes/', include('accounting.urls.safes')),
    path('customers/', include('accounting.urls.customers')),
    path('suppliers/', include('accounting.urls.suppliers')),
    path('units/', include('accounting.urls.units')),
    path('projects/', include('accounting.urls.projects_store')),
    path('contracts/', include('accounting.urls.contracts')),
    path('installments/', include('accounting.urls.installments')),
    path('vouchers/', include('accounting.urls.vouchers')),
    path('settlements/', include('accounting.urls.settlements')),
    
    # New Modules
    path('brokers/', include('accounting.urls.brokers')),
    path('transfers/', include('accounting.urls.transfers')),
    path('treasury/', include('accounting.urls.treasury')),
    path('partner-debts/', include('accounting.urls.partner_debts')),
    
    # Reports & Analytics
    path('reports/', include('accounting.urls.reports')),
    
    # System
    path('audit/', include('accounting.urls.audit')),
    path('backup/', include('accounting.urls.backup')),
    path('settings/', include('accounting.urls.settings')),
    
    # API Endpoints
    path('api/undo/', undo_action, name='api_undo_action'),
    path('api/redo/', redo_action, name='api_redo_action'),
    path('api/theme/', update_theme, name='api_update_theme'),
    path('api/search/', global_search, name='api_global_search'),
    path('api/lock/', lock_app, name='api_lock_app'),
    path('api/unlock/', unlock_app, name='api_unlock_app'),
]
