import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import ProtectedError

from accounting.models import Project, Item, StockMove
from accounting.forms import ProjectForm, ItemForm, StockMoveForm

# --- Project Views ---

@login_required
def project_list_view(request):
    form = ProjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        project = form.save()
        response = render(request, 'accounting/projects/_row.html', {'project': project})
        response['HX-Retarget'] = '#project-table-body'
        response['HX-Reswap'] = 'afterbegin'
        form_response = render(request, 'accounting/projects/_form_container.html', {'form': ProjectForm()})
        response.content += form_response.content
        return response

    projects = Project.objects.all()
    context = {
        'projects': projects,
        'form': form,
        'page_title': 'المشاريع'
    }
    return render(request, 'accounting/projects/list.html', context)

@login_required
@require_POST
def project_update_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST, instance=project)
    if form.is_valid():
        project = form.save()
        return render(request, 'accounting/projects/_row.html', {'project': project})
    return render(request, 'accounting/projects/_form_container.html', {'form': form, 'project': project})

@login_required
def project_get_form_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(instance=project)
    return render(request, 'accounting/projects/_form_container.html', {'form': form, 'project': project})

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
    form = ItemForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save()
        item.balance = 0
        response = render(request, 'accounting/store/_item_row.html', {'item': item})
        response['HX-Retarget'] = '#item-table-body'
        response['HX-Reswap'] = 'afterbegin'
        form_response = render(request, 'accounting/store/_form_container.html', {'form': ItemForm()})
        response.content += form_response.content
        return response

    items = Item.objects.select_related('supplier').all()
    for item in items:
        item.balance = item.get_stock_balance()
    context = {
        'items': items,
        'form': form,
        'page_title': 'أصناف المخزن'
    }
    return render(request, 'accounting/store/items.html', context)

@login_required
@require_POST
def item_update_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    form = ItemForm(request.POST, instance=item)
    if form.is_valid():
        item = form.save()
        item.balance = item.get_stock_balance()
        return render(request, 'accounting/store/_item_row.html', {'item': item})
    return render(request, 'accounting/store/_form_container.html', {'form': form, 'item': item})

@login_required
def item_get_form_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    form = ItemForm(instance=item)
    return render(request, 'accounting/store/_form_container.html', {'form': form, 'item': item})

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
    form = StockMoveForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        toast_event = {"showToast": {"message": "تم تسجيل حركة المخزن بنجاح!", "type": "success"}}
        response = HttpResponse()
        response['HX-Trigger-After-Swap'] = json.dumps(toast_event)
        response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/')
        return response

    moves = StockMove.objects.select_related('item', 'project').all()
    context = {
        'moves': moves,
        'form': form,
        'page_title': 'حركة المخزن'
    }
    return render(request, 'accounting/store/moves.html', context)
