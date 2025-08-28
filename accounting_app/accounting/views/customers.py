from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import ProtectedError

from accounting.models import Customer
from accounting.forms import CustomerForm

@login_required
def customer_list_view(request):
    """
    Renders the list of all customers and handles creation of a new customer.
    """
    form = CustomerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        customer = form.save()
        # Return the new row and a cleared form
        response = render(request, 'accounting/customers/_row.html', {'customer': customer})
        # HTMX can handle multiple swaps, here we append to the table and replace the form
        response['HX-Retarget'] = '#customer-table-body'
        response['HX-Reswap'] = 'afterbegin'
        # We need another response to clear the form
        form_response = render(request, 'accounting/customers/_form_container.html', {'form': CustomerForm()})
        response.content += form_response.content
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
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST, instance=customer)
    if form.is_valid():
        customer = form.save()
        # Return the updated row to be swapped in the table
        return render(request, 'accounting/customers/_row.html', {'customer': customer})
    # If form is invalid, return the form with errors
    return render(request, 'accounting/customers/_form_container.html', {'form': form, 'customer': customer})

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
