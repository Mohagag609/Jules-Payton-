from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from accounting.models import Safe
from accounting.forms import SafeForm
from accounting.services.treasury import get_safe_balance

@login_required
def safe_list_view(request):
    """
    Renders the list of all safes along with their current balances.
    """
    safes = Safe.objects.select_related('partner').all()
    # Add balance to each safe object
    for safe in safes:
        safe.balance = get_safe_balance(safe)

    context = {
        'safes': safes,
        'page_title': 'الخزائن والمحافظ'
    }
    return render(request, 'accounting/safes/list.html', context)

@login_required
def safe_create_view(request):
    """
    Handles creation of a new safe.
    """
    if request.method == 'POST':
        form = SafeForm(request.POST)
        if form.is_valid():
            safe = form.save()
            safe.balance = get_safe_balance(safe) # Calculate initial balance (should be 0)
            return render(request, 'accounting/safes/_row.html', {'safe': safe})
    else:
        form = SafeForm()

    context = {'form': form}
    return render(request, 'accounting/safes/_form.html', context)

@login_required
def safe_edit_view(request, pk):
    """
    Handles editing an existing safe.
    """
    safe = get_object_or_404(Safe, pk=pk)
    if request.method == 'POST':
        form = SafeForm(request.POST, instance=safe)
        if form.is_valid():
            safe = form.save()
            safe.balance = get_safe_balance(safe)
            return render(request, 'accounting/safes/_row.html', {'safe': safe})
    else:
        form = SafeForm(instance=safe)

    context = {
        'form': form,
        'safe': safe
    }
    return render(request, 'accounting/safes/_form.html', context)

@login_required
@require_http_methods(["DELETE"])
def safe_delete_view(request, pk):
    """
    Handles deletion of a safe.
    """
    safe = get_object_or_404(Safe, pk=pk)
    # Add a check here to prevent deleting a safe with a balance or transactions
    balance = get_safe_balance(safe)
    if balance != 0 or safe.receiptvoucher_set.exists() or safe.paymentvoucher_set.exists():
         # In a real app, you'd return an error message to the user.
         # For now, we just prevent deletion.
         # Returning the row itself to prevent deletion on the frontend.
        safe.balance = balance
        return render(request, 'accounting/safes/_row.html', {'safe': safe})

    safe.delete()
    return HttpResponse()
