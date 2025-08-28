from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
import json
import logging

from accounting.models import Customer
from accounting.forms import CustomerForm
from .base import HTMXResponseMixin

logger = logging.getLogger('accounting')


class CustomerViewMixin(HTMXResponseMixin):
    """Mixin for customer views"""
    pass


@login_required
def customer_list_view(request):
    """
    Renders the list of all customers and handles creation of a new customer.
    """
    mixin = CustomerViewMixin()
    form = CustomerForm(request.POST or None)
    
    if request.method == 'POST':
        response = mixin.handle_form_submission(
            request=request,
            form=form,
            success_template='accounting/customers/_row.html',
            form_template='accounting/customers/_form_container.html',
            object_name='customer',
            success_message='تم إضافة العميل بنجاح!',
            htmx_trigger='customerAdded'
        )
        return response

    customers = Customer.objects.all()
    context = {
        'customers': customers,
        'form': form,
        'page_title': 'العملاء'
    }
    return render(request, 'accounting/customers/list.html', context)


@login_required
@require_POST
def customer_update_view(request, pk):
    """
    Handles updating an existing customer.
    """
    mixin = CustomerViewMixin()
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST, instance=customer)
    
    return mixin.handle_update(
        request=request,
        form=form,
        instance=customer,
        success_template='accounting/customers/_row.html',
        form_template='accounting/customers/_form_container.html',
        object_name='customer',
        success_message=f'تم تحديث بيانات العميل "{customer.name}" بنجاح!'
    )


@login_required
def customer_get_form_view(request, pk):
    """
    Returns the customer form pre-filled with data for editing.
    """
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(instance=customer)
    return render(request, 'accounting/customers/_form_container.html', {'form': form, 'customer': customer})


@login_required
@require_http_methods(["DELETE"])
def customer_delete_view(request, pk):
    """
    Handles deletion of a customer.
    """
    mixin = CustomerViewMixin()
    customer = get_object_or_404(Customer, pk=pk)
    
    response = mixin.handle_delete(
        request=request,
        instance=customer,
        object_name='العميل',
        success_message=f'تم حذف العميل "{customer.name}" بنجاح!'
    )
    
    # Add HTMX trigger for toast notification
    if response.status_code == 200:
        toast_event = {
            "showToast": {
                "message": f'تم حذف العميل "{customer.name}" بنجاح!',
                "type": "success"
            }
        }
        response['HX-Trigger'] = json.dumps(toast_event)
    else:
        toast_event = {
            "showToast": {
                "message": "لا يمكن حذف هذا العميل لأنه مرتبط بعقود أو سندات.",
                "type": "error"
            }
        }
        response['HX-Trigger'] = json.dumps(toast_event)
    
    return response