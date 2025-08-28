"""
Audit Log Views
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import csv

from accounting.models import AuditLog


@login_required
def audit_log_list(request):
    """List audit logs"""
    logs = AuditLog.objects.all().select_related('user').order_by('-timestamp')
    
    # Filters
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    return render(request, 'accounting/audit/list.html', {
        'logs': logs[:100]  # Limit to 100 most recent
    })


@login_required
def audit_log_export(request):
    """Export audit logs to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_log.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['التاريخ', 'المستخدم', 'الإجراء', 'الوصف', 'IP'])
    
    logs = AuditLog.objects.all().select_related('user').order_by('-timestamp')[:1000]
    
    for log in logs:
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.user.username if log.user else 'نظام',
            log.get_action_display(),
            log.description,
            log.ip_address or ''
        ])
    
    return response