from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    Customer, Unit, Partner, PartnersGroup, Contract, Installment,
    Safe, ReceiptVoucher, PaymentVoucher, Broker, BrokerDue,
    UnitPartner, Transfer, PartnerDebt, UserSettings, AuditLog
)


@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    list_display = ['code', 'name', 'phone', 'national_id', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['code', 'name', 'phone', 'national_id']
    readonly_fields = ['created_at']


@admin.register(Unit)
class UnitAdmin(ImportExportModelAdmin):
    list_display = ['code', 'name', 'building_no', 'floor', 'type', 'status', 'price_total']
    list_filter = ['type', 'status', 'category']
    search_fields = ['code', 'name', 'building_no']
    readonly_fields = ['created_at']


@admin.register(Broker)
class BrokerAdmin(ImportExportModelAdmin):
    list_display = ['name', 'phone', 'created_at']
    search_fields = ['name', 'phone']
    readonly_fields = ['created_at']


@admin.register(BrokerDue)
class BrokerDueAdmin(admin.ModelAdmin):
    list_display = ['broker_name', 'contract', 'amount', 'due_date', 'status', 'payment_date']
    list_filter = ['status', 'due_date']
    search_fields = ['broker_name', 'contract__code']
    readonly_fields = ['created_at']


@admin.register(UnitPartner)
class UnitPartnerAdmin(admin.ModelAdmin):
    list_display = ['unit', 'partner', 'percent', 'created_at']
    list_filter = ['created_at']
    search_fields = ['unit__code', 'unit__name', 'partner__name']
    readonly_fields = ['created_at']


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ['from_safe', 'to_safe', 'amount', 'date', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['from_safe__name', 'to_safe__name', 'notes']
    readonly_fields = ['created_at']


@admin.register(PartnerDebt)
class PartnerDebtAdmin(admin.ModelAdmin):
    list_display = ['paying_partner', 'owed_partner', 'unit', 'amount', 'due_date', 'status']
    list_filter = ['status', 'due_date']
    search_fields = ['paying_partner__name', 'owed_partner__name', 'unit__code']
    readonly_fields = ['created_at']


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'font_size', 'is_locked', 'updated_at']
    list_filter = ['theme', 'is_locked']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'description', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['description', 'user__username']
    readonly_fields = ['timestamp', 'user', 'action', 'description', 'content_type', 'object_id', 'details', 'ip_address', 'user_agent']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
