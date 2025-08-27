import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import ProtectedError

from accounting.models import Supplier
from accounting.forms import SupplierForm

@login_required
def supplier_list_view(request):
    suppliers = Supplier.objects.all()
    context = {
        'suppliers': suppliers,
        'page_title': 'الموردون'
    }
    return render(request, 'accounting/suppliers/list.html', context)

@login_required
def supplier_create_view(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            response = render(request, 'accounting/suppliers/_row.html', {'supplier': supplier})
            response['HX-Trigger'] = json.dumps({"closeModal": None, "showToast": {"message": "تم إنشاء المورد بنجاح!", "type": "success"}})
            return response
    else:
        form = SupplierForm()
    context = {'form': form}
    return render(request, 'accounting/suppliers/_form.html', context)

@login_required
def supplier_edit_view(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            response = render(request, 'accounting/suppliers/_row.html', {'supplier': supplier})
            response['HX-Trigger'] = json.dumps({"closeModal": None, "showToast": {"message": "تم تحديث المورد بنجاح!", "type": "success"}})
            return response
    else:
        form = SupplierForm(instance=supplier)
    context = {
        'form': form,
        'supplier': supplier
    }
    return render(request, 'accounting/suppliers/_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def supplier_delete_view(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    try:
        supplier.delete()
        response = HttpResponse()
        toast_event = {"showToast": {"message": f"تم حذف المورد '{supplier.name}' بنجاح.", "type": "success"}}
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
    except ProtectedError:
        response = HttpResponse()
        toast_event = {"showToast": {"message": "لا يمكن حذف هذا المورد لأنه مرتبط بسندات أو أصناف.", "type": "error"}}
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
