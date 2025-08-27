import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import ProtectedError

from accounting.models import Project, Item, StockMove
from accounting.forms import ProjectForm, ItemForm, StockMoveForm

# --- Project Views ---

@login_required
def project_list_view(request):
    projects = Project.objects.all()
    return render(request, 'accounting/projects/list.html', {'projects': projects, 'page_title': 'المشاريع'})

@login_required
def project_create_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return render(request, 'accounting/projects/_row.html', {'project': project})
    else:
        form = ProjectForm()
    return render(request, 'accounting/projects/_form.html', {'form': form})

@login_required
def project_edit_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            return render(request, 'accounting/projects/_row.html', {'project': project})
    else:
        form = ProjectForm(instance=project)
    return render(request, 'accounting/projects/_form.html', {'form': form, 'project': project})

@login_required
@require_http_methods(["DELETE"])
def project_delete_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    try:
        project.delete()
        response = HttpResponse()
        toast_event = {"showToast": {"message": f"تم حذف المشروع '{project.name}' بنجاح.", "type": "success"}}
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
    except ProtectedError:
        response = HttpResponse()
        toast_event = {"showToast": {"message": "لا يمكن حذف هذا المشروع لأنه مرتبط بسندات صرف أو حركات مخزن.", "type": "error"}}
        response['HX-Trigger'] = json.dumps(toast_event)
        return response

# --- Item (Store) Views ---

@login_required
def item_list_view(request):
    items = Item.objects.select_related('supplier').all()
    for item in items:
        item.balance = item.get_stock_balance()
    return render(request, 'accounting/store/items.html', {'items': items, 'page_title': 'أصناف المخزن'})

@login_required
def item_create_view(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            item.balance = 0
            return render(request, 'accounting/store/_item_row.html', {'item': item})
    else:
        form = ItemForm()
    return render(request, 'accounting/store/_item_form.html', {'form': form})

@login_required
def item_edit_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            item.balance = item.get_stock_balance()
            return render(request, 'accounting/store/_item_row.html', {'item': item})
    else:
        form = ItemForm(instance=item)
    return render(request, 'accounting/store/_item_form.html', {'form': form, 'item': item})

@login_required
@require_http_methods(["DELETE"])
def item_delete_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    try:
        item.delete()
        response = HttpResponse()
        toast_event = {"showToast": {"message": f"تم حذف الصنف '{item.name}' بنجاح.", "type": "success"}}
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
    except ProtectedError:
        response = HttpResponse()
        toast_event = {"showToast": {"message": "لا يمكن حذف هذا الصنف لأنه مرتبط بحركات مخزن.", "type": "error"}}
        response['HX-Trigger'] = json.dumps(toast_event)
        return response

# --- Stock Move Views ---

@login_required
def stock_move_list_view(request):
    moves = StockMove.objects.select_related('item', 'project').all()
    return render(request, 'accounting/store/moves.html', {'moves': moves, 'page_title': 'حركة المخزن'})

@login_required
def stock_move_create_view(request):
    if request.method == 'POST':
        form = StockMoveForm(request.POST)
        if form.is_valid():
            form.save()
            # This is a bit different, we redirect to the list view
            # as there isn't a single row to update easily.
            response = HttpResponse()
            response['HX-Redirect'] = request.META.get('HTTP_REFERER')
            return response
    else:
        form = StockMoveForm()
    # This form is often better on its own page or a dedicated modal
    return render(request, 'accounting/store/_move_form.html', {'form': form})
