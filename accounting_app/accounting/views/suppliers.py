from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
import json
import logging

from accounting.models import Supplier
from accounting.forms import SupplierForm
from .base import HTMXResponseMixin

logger = logging.getLogger('accounting')


class SupplierViewMixin(HTMXResponseMixin):
    """Mixin for supplier views"""
    pass


@login_required
def supplier_list_view(request):
    """List all suppliers and handle creation"""
    mixin = SupplierViewMixin()
    form = SupplierForm(request.POST or None)
    
    if request.method == 'POST':
        response = mixin.handle_form_submission(
            request=request,
            form=form,
            success_template='accounting/suppliers/_row.html',
            form_template='accounting/suppliers/_form_container.html',
            object_name='supplier',
            success_message='تم إضافة المورد بنجاح!',
            htmx_trigger='supplierAdded'
        )
        return response

    suppliers = Supplier.objects.all()
    context = {
        'suppliers': suppliers,
        'form': form,
        'page_title': 'الموردين'
    }
    return render(request, 'accounting/suppliers/list.html', context)


@login_required
@require_POST
def supplier_update_view(request, pk):
    """Update supplier"""
    mixin = SupplierViewMixin()
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST, instance=supplier)
    
    return mixin.handle_update(
        request=request,
        form=form,
        instance=supplier,
        success_template='accounting/suppliers/_row.html',
        form_template='accounting/suppliers/_form_container.html',
        object_name='supplier',
        success_message=f'تم تحديث بيانات المورد "{supplier.name}" بنجاح!'
    )


@login_required
def supplier_get_form_view(request, pk):
    """Get supplier form for editing"""
    supplier = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(instance=supplier)
    return render(request, 'accounting/suppliers/_form_container.html', {'form': form, 'supplier': supplier})


@login_required
@require_http_methods(["DELETE"])
def supplier_delete_view(request, pk):
    """Delete supplier"""
    mixin = SupplierViewMixin()
    supplier = get_object_or_404(Supplier, pk=pk)
    
    response = mixin.handle_delete(
        request=request,
        instance=supplier,
        object_name='المورد',
        success_message=f'تم حذف المورد "{supplier.name}" بنجاح!'
    )
    
    # Add HTMX trigger for toast notification
    if response.status_code == 200:
        toast_event = {
            "showToast": {
                "message": f'تم حذف المورد "{supplier.name}" بنجاح!',
                "type": "success"
            }
        }
        response['HX-Trigger'] = json.dumps(toast_event)
    else:
        toast_event = {
            "showToast": {
                "message": "لا يمكن حذف هذا المورد لأنه مرتبط بسندات أو فواتير.",
                "type": "error"
            }
        }
        response['HX-Trigger'] = json.dumps(toast_event)
    
    return response