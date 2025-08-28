from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import ProtectedError

from accounting.models import Safe
from accounting.forms import SafeForm
from accounting.services.treasury import get_safe_balance

@login_required
def safe_list_view(request):
    form = SafeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        safe = form.save()
        safe.balance = get_safe_balance(safe)
        response = render(request, 'accounting/safes/_row.html', {'safe': safe})
        response['HX-Retarget'] = '#safe-table-body'
        response['HX-Reswap'] = 'afterbegin'
        form_response = render(request, 'accounting/safes/_form_container.html', {'form': SafeForm()})
        response.content += form_response.content
        return response

    safes = Safe.objects.select_related('partner').all()
    for safe in safes:
        safe.balance = get_safe_balance(safe)
    context = {
        'safes': safes,
        'form': form,
        'page_title': 'الخزائن والمحافظ'
    }
    return render(request, 'accounting/safes/list.html', context)

@login_required
@require_POST
def safe_update_view(request, pk):
    safe = get_object_or_404(Safe, pk=pk)
    form = SafeForm(request.POST, instance=safe)
    if form.is_valid():
        safe = form.save()
        safe.balance = get_safe_balance(safe)
        return render(request, 'accounting/safes/_row.html', {'safe': safe})
    return render(request, 'accounting/safes/_form_container.html', {'form': form, 'safe': safe})

@login_required
def safe_get_form_view(request, pk):
    safe = get_object_or_404(Safe, pk=pk)
    form = SafeForm(instance=safe)
    return render(request, 'accounting/safes/_form_container.html', {'form': form, 'safe': safe})

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
