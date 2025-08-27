from django.urls import path
from accounting.views import installments as views

app_name = 'installments'

urlpatterns = [
    path('', views.installment_list_view, name='list'),
    path('<int:pk>/pay/', views.installment_pay_view, name='pay'),
]
