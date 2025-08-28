from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import ProtectedError

from accounting.models import Supplier
from accounting.forms import SupplierForm

@login_required
def supplier_list_view(request):
    form = SupplierForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        supplier = form.save()
        response = render(request, 'accounting/suppliers/_row.html', {'supplier': supplier})
        response['HX-Retarget'] = '#supplier-table-body'
        response['HX-Reswap'] = 'afterbegin'
        form_response = render(request, 'accounting/suppliers/_form_container.html', {'form': SupplierForm()})
        response.content += form_response.content
        return response

    suppliers = Supplier.objects.all()
    context = {
        'suppliers': suppliers,
        'form': form,
        'page_title': 'الموردون'
    }
    return render(request, 'accounting/suppliers/list.html', context)

@login_required
@require_POST
def supplier_update_view(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST, instance=supplier)
    if form.is_valid():
        supplier = form.save()
        return render(request, 'accounting/suppliers/_row.html', {'supplier': supplier})
    return render(request, 'accounting/suppliers/_form_container.html', {'form': form, 'supplier': supplier})

@login_required
def supplier_get_form_view(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(instance=supplier)
    return render(request, 'accounting/suppliers/_form_container.html', {'form': form, 'supplier': supplier})

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
