"""
Backup Views
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import json

from accounting.services.import_export import ImportExportService


@login_required
def backup_dashboard(request):
    """Backup dashboard"""
    return render(request, 'accounting/backup/dashboard.html')


@login_required
def backup_export(request):
    """Export backup"""
    try:
        backup_data = ImportExportService.backup_all_data(user=request.user)
        
        response = HttpResponse(
            backup_data,
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="backup.json"'
        
        return response
    except Exception as e:
        messages.error(request, f'خطأ في إنشاء النسخة الاحتياطية: {str(e)}')
        return redirect('backup:backup_dashboard')


@login_required
def backup_restore(request):
    """Restore from backup"""
    if request.method == 'POST':
        # Handle file upload and restore
        messages.info(request, 'ميزة الاستعادة قيد التطوير')
    
    return render(request, 'accounting/backup/restore.html')