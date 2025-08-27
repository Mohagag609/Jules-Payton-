from django.urls import path
from accounting.views import vouchers as views

app_name = 'vouchers'

urlpatterns = [
    path('receipts/', views.receipt_voucher_list_view, name='receipt_list'),
    path('receipts/create/', views.receipt_voucher_create_view, name='receipt_create'),

    path('payments/', views.payment_voucher_list_view, name='payment_list'),
    path('payments/create/', views.payment_voucher_create_view, name='payment_create'),
]
