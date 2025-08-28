from django.urls import path, include
from accounting.views import dashboard

app_name = 'accounting'

urlpatterns = [
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
    path('api/undo/', dashboard.undo_action, name='api_undo_action'),
    path('api/redo/', dashboard.redo_action, name='api_redo_action'),
    path('api/theme/', dashboard.update_theme, name='api_update_theme'),
    path('api/search/', dashboard.global_search, name='api_global_search'),
    path('api/lock/', dashboard.lock_app, name='lock_app'),
    path('api/unlock/', dashboard.unlock_app, name='unlock_app'),
]
