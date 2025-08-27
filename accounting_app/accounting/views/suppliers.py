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
    """
    Renders the list of all suppliers.
    """
    suppliers = Supplier.objects.all()
    context = {
        'suppliers': suppliers,
        'page_title': 'الموردون'
    }
    return render(request, 'accounting/suppliers/list.html', context)

@login_required
def supplier_create_view(request):
    """
    Handles creation of a new supplier.
    """
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
    """
    Handles editing an existing supplier.
    """
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
    """
    Handles deletion of a supplier.
    """
    supplier = get_object_or_404(Supplier, pk=pk)
    try:
        supplier.delete()
    except ProtectedError:
        # This will happen if the supplier is linked to items or vouchers.
        pass

    return HttpResponse()
