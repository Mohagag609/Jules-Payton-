import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import ProtectedError

from accounting.models import Partner
from accounting.forms import PartnerForm

@login_required
def partner_list_view(request):
    """
    Renders the list of all partners.
    """
    partners = Partner.objects.all()
    context = {
        'partners': partners,
        'page_title': 'الشركاء'
    }
    return render(request, 'accounting/partners/list.html', context)

@login_required
def partner_create_view(request):
    """
    Handles creation of a new partner.
    GET: Returns the form to be loaded into the modal.
    POST: Processes the form and returns the new table row, closing the modal.
    """
    if request.method == 'POST':
        form = PartnerForm(request.POST)
        if form.is_valid():
            partner = form.save()
            response = render(request, 'accounting/partners/_row.html', {'partner': partner})
            response['HX-Trigger'] = json.dumps({"closeModal": None, "showToast": {"message": "تم إنشاء الشريك بنجاح!", "type": "success"}})
            return response
    else:
        form = PartnerForm()

    context = {'form': form}
    return render(request, 'accounting/partners/_form.html', context)

@login_required
def partner_edit_view(request, pk):
    """
    Handles editing an existing partner.
    """
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == 'POST':
        form = PartnerForm(request.POST, instance=partner)
        if form.is_valid():
            partner = form.save()
            response = render(request, 'accounting/partners/_row.html', {'partner': partner})
            response['HX-Trigger'] = json.dumps({"closeModal": None, "showToast": {"message": "تم تحديث بيانات الشريك بنجاح!", "type": "success"}})
            return response
    else:
        form = PartnerForm(instance=partner)

    context = {
        'form': form,
        'partner': partner
    }
    return render(request, 'accounting/partners/_form.html', context)


@login_required
@require_http_methods(["DELETE"])
def partner_delete_view(request, pk):
    """
    Handles deletion of a partner.
    """
    partner = get_object_or_404(Partner, pk=pk)
    try:
        partner.delete()
        response = HttpResponse()
        toast_event = {
            "showToast": {
                "message": f"تم حذف الشريك '{partner.name}' بنجاح.",
                "type": "success"
            }
        }
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
    except ProtectedError:
        response = HttpResponse()
        toast_event = {
            "showToast": {
                "message": "لا يمكن حذف هذا الشريك لأنه مرتبط بمجموعات أو محافظ.",
                "type": "error"
            }
        }
        response['HX-Trigger'] = json.dumps(toast_event)
        return response
