"""
Settings URLs
"""

from django.urls import path
from accounting.views import settings as views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_view, name='settings_view'),
    path('profile/', views.profile_view, name='profile_view'),
]