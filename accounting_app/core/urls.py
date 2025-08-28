from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-styles/', TemplateView.as_view(template_name='test_styles.html'), name='test_styles'),
    path('', include('accounting.urls')),
    path("health/", lambda r: HttpResponse("ok")),
]
