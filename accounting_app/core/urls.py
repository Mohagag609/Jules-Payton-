from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import redirect

def home_redirect(request):
    """Redirect home to dashboard or login"""
    if request.user.is_authenticated:
        return redirect('accounting:dashboard')
    return redirect('admin:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('accounting/', include('accounting.urls')),
    path("health/", lambda r: HttpResponse("ok")),
]
