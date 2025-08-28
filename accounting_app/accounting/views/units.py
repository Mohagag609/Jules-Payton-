from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import ProtectedError

from accounting.models import Unit
from accounting.forms import UnitForm

@login_required
def unit_list_view(request):
    form = UnitForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        unit = form.save()
        response = render(request, 'accounting/units/_row.html', {'unit': unit})
        response['HX-Retarget'] = '#unit-table-body'
        response['HX-Reswap'] = 'afterbegin'
        form_response = render(request, 'accounting/units/_form_container.html', {'form': UnitForm()})
        response.content += form_response.content
        return response

    units = Unit.objects.select_related('partners_group', 'contract').all()
    context = {
        'units': units,
        'form': form,
        'page_title': 'الوحدات'
    }
    return render(request, 'accounting/units/list.html', context)

@login_required
@require_POST
def unit_update_view(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    form = UnitForm(request.POST, instance=unit)
    if form.is_valid():
        unit = form.save()
        return render(request, 'accounting/units/_row.html', {'unit': unit})
    return render(request, 'accounting/units/_form_container.html', {'form': form, 'unit': unit})

@login_required
def unit_get_form_view(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    form = UnitForm(instance=unit)
    return render(request, 'accounting/units/_form_container.html', {'form': form, 'unit': unit})

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
