import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import ProtectedError

from accounting.models import Safe
from accounting.forms import SafeForm
from accounting.services.treasury import get_safe_balance

@login_required
def safe_list_view(request):
    safes = Safe.objects.select_related('partner').all()
    for safe in safes:
        safe.balance = get_safe_balance(safe)
    context = {
        'safes': safes,
        'page_title': 'الخزائن والمحافظ'
    }
    return render(request, 'accounting/safes/list.html', context)

@login_required
def safe_create_view(request):
    if request.method == 'POST':
        form = SafeForm(request.POST)
        if form.is_valid():
            safe = form.save()
            safe.balance = get_safe_balance(safe)
            response = render(request, 'accounting/safes/_row.html', {'safe': safe})
            response['HX-Trigger'] = json.dumps({"closeModal": None, "showToast": {"message": "تم إنشاء الخزنة بنجاح!", "type": "success"}})
            return response
    else:
        form = SafeForm()
    context = {'form': form}
    return render(request, 'accounting/safes/_form.html', context)

@login_required
def safe_edit_view(request, pk):
    safe = get_object_or_404(Safe, pk=pk)
    if request.method == 'POST':
        form = SafeForm(request.POST, instance=safe)
        if form.is_valid():
            safe = form.save()
            safe.balance = get_safe_balance(safe)
            response = render(request, 'accounting/safes/_row.html', {'safe': safe})
            response['HX-Trigger'] = json.dumps({"closeModal": None, "showToast": {"message": "تم تحديث الخزنة بنجاح!", "type": "success"}})
            return response
    else:
        form = SafeForm(instance=safe)
    context = {
        'form': form,
        'safe': safe
    }
    return render(request, 'accounting/safes/_form.html', context)

@login_required
@require_http_methods(["DELETE"])
def safe_delete_view(request, pk):
    safe = get_object_or_404(Safe, pk=pk)
    try:
        safe.delete()
        response = HttpResponse()
        toast_event = {"showToast": {"message": f"تم حذف '{safe.name}' بنجاح.", "type": "success"}}
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
    except ProtectedError:
        response = HttpResponse()
        toast_event = {"showToast": {"message": "لا يمكن حذف خزنة مرتبطة بسندات. قم بنقل الرصيد والمعاملات أولاً.", "type": "error"}}
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
