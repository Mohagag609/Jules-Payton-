from django.urls import path
from accounting.views import reports as views

app_name = 'reports'

urlpatterns = [
    path('', views.report_index_view, name='index'),
    path('treasury/', views.treasury_report_view, name='treasury'),
    # Add other report URLs here
]
