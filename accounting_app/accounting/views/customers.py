from django.shortcuts import render, get_object_or_404
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
    except ProtectedError:
        # This will happen if the customer is linked to a contract.
        # In a real app, you would send a message back to the user.
        # For now, we just prevent deletion and do nothing, so the row remains.
        # You could also use Django's messages framework and an HTMX header to show a toast.
        pass

    return HttpResponse()
