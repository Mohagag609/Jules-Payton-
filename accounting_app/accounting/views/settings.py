"""
Settings Views
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounting.models import UserSettings
from accounting.forms import UserSettingsForm


@login_required
def settings_view(request):
    """User settings view"""
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ الإعدادات بنجاح')
            return redirect('settings:settings_view')
    else:
        form = UserSettingsForm(instance=settings)
    
    return render(request, 'accounting/settings/form.html', {
        'form': form,
        'settings': settings
    })


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'accounting/settings/profile.html', {
        'user': request.user
    })