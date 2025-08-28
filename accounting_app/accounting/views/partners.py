from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import ProtectedError

from accounting.models import Partner
from accounting.forms import PartnerForm

@login_required
def partner_list_view(request):
    """
    Renders the list of all partners and handles creation of a new partner.
    """
    form = PartnerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        partner = form.save()
        response = render(request, 'accounting/partners/_row.html', {'partner': partner})
        response['HX-Retarget'] = '#partner-table-body'
        response['HX-Reswap'] = 'afterbegin'
        form_response = render(request, 'accounting/partners/_form_container.html', {'form': PartnerForm()})
        response.content += form_response.content
        return response

    partners = Partner.objects.all()
    context = {
        'partners': partners,
        'form': form,
        'page_title': 'الشركاء'
    }
    return render(request, 'accounting/partners/list.html', context)

@login_required
@require_POST
def partner_update_view(request, pk):
    """
    Handles updating an existing partner.
    """
    partner = get_object_or_404(Partner, pk=pk)
    form = PartnerForm(request.POST, instance=partner)
    if form.is_valid():
        partner = form.save()
        return render(request, 'accounting/partners/_row.html', {'partner': partner})
    return render(request, 'accounting/partners/_form_container.html', {'form': form, 'partner': partner})

@login_required
def partner_get_form_view(request, pk):
    """
    Returns the partner form pre-filled with data for editing.
    """
    partner = get_object_or_404(Partner, pk=pk)
    form = PartnerForm(instance=partner)
    return render(request, 'accounting/partners/_form_container.html', {'form': form, 'partner': partner})

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
