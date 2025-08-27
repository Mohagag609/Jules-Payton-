import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import ProtectedError

from accounting.models import Unit
from accounting.forms import UnitForm

@login_required
def unit_list_view(request):
    units = Unit.objects.select_related('partners_group', 'contract').all()
    context = {
        'units': units,
        'page_title': 'الوحدات'
    }
    return render(request, 'accounting/units/list.html', context)

@login_required
def unit_create_view(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            response = render(request, 'accounting/units/_row.html', {'unit': unit})
            response['HX-Trigger'] = json.dumps({"closeModal": None, "showToast": {"message": "تم إنشاء الوحدة بنجاح!", "type": "success"}})
            return response
    else:
        form = UnitForm()
    context = {'form': form}
    return render(request, 'accounting/units/_form.html', context)

@login_required
def unit_edit_view(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            unit = form.save()
            response = render(request, 'accounting/units/_row.html', {'unit': unit})
            response['HX-Trigger'] = json.dumps({"closeModal": None, "showToast": {"message": "تم تحديث الوحدة بنجاح!", "type": "success"}})
            return response
    else:
        form = UnitForm(instance=unit)
    context = {
        'form': form,
        'unit': unit
    }
    return render(request, 'accounting/units/_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def unit_delete_view(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    try:
        unit.delete()
        response = HttpResponse()
        toast_event = {"showToast": {"message": f"تم حذف الوحدة '{unit.name}' بنجاح.", "type": "success"}}
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
    except ProtectedError:
        response = HttpResponse()
        toast_event = {"showToast": {"message": "لا يمكن حذف هذه الوحدة لأنها مرتبطة بعقد.", "type": "error"}}
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
