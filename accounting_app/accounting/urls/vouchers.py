from django.urls import path
from accounting.views import vouchers as views

app_name = 'vouchers'

urlpatterns = [
    path('receipts/', views.receipt_voucher_list_view, name='receipt_list'),
    path('payments/', views.payment_voucher_list_view, name='payment_list'),
]
