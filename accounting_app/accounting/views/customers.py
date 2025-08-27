from django.shortcuts import render, get_object_or_404
import json
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import ProtectedError
from django.contrib import messages

from accounting.models import Customer
from accounting.forms import CustomerForm

@login_required
def customer_list_view(request):
    """
    Renders the list of all customers.
    """
    customers = Customer.objects.all()
    context = {
        'customers': customers,
        'page_title': 'العملاء'
    }
    return render(request, 'accounting/customers/list.html', context)

@login_required
def customer_create_view(request):
    """
    Handles creation of a new customer.
    """
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return render(request, 'accounting/customers/_row.html', {'customer': customer})
    else:
        form = CustomerForm()

    context = {'form': form}
    return render(request, 'accounting/customers/_form.html', context)

@login_required
def customer_edit_view(request, pk):
    """
    Handles editing an existing customer.
    """
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            return render(request, 'accounting/customers/_row.html', {'customer': customer})
    else:
        form = CustomerForm(instance=customer)

    context = {
        'form': form,
        'customer': customer
    }
    return render(request, 'accounting/customers/_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def customer_delete_view(request, pk):
    """
    Handles deletion of a customer.
    """
    customer = get_object_or_404(Customer, pk=pk)
    try:
        customer.delete()
        # On successful deletion, HTMX will remove the element.
        # We can also send a success toast.
        response = HttpResponse()
        toast_event = {
            "showToast": {
                "message": f"تم حذف العميل '{customer.name}' بنجاح.",
                "type": "success"
            }
        }
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
    except ProtectedError:
        # On failure, we return a 200 OK but trigger an error toast.
        # The row will not be removed from the DOM.
        response = HttpResponse()
        toast_event = {
            "showToast": {
                "message": "لا يمكن حذف هذا العميل لأنه مرتبط بعقود أو سندات.",
                "type": "error"
            }
        }
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
