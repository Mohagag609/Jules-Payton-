from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from accounting.models import PartnersGroup, Project, Settlement
from accounting.services.settlements import calculate_partner_settlement

@login_required
def settlement_list_view(request):
    settlements = Settlement.objects.select_related('project').all()
    context = {
        'settlements': settlements,
        'page_title': 'سجل التسويات'
    }
    return render(request, 'accounting/settlements/list.html', context)

@login_required
def settlement_detail_view(request, pk):
    settlement = get_object_or_404(Settlement, pk=pk)
    context = {
        'settlement': settlement,
        'page_title': f'تفاصيل التسوية رقم {settlement.pk}'
    }
    return render(request, 'accounting/settlements/detail.html', context)

@login_required
def settlement_create_view(request):
    if request.method == 'POST':
        try:
            group_id = request.POST.get('group')
            from_date = date.fromisoformat(request.POST.get('from_date'))
            to_date = date.fromisoformat(request.POST.get('to_date'))
            project_id = request.POST.get('project') if request.POST.get('project') else None

            group = get_object_or_404(PartnersGroup, pk=group_id)

            settlement = calculate_partner_settlement(
                partners_group=group,
                from_date=from_date,
                to_date=to_date,
                project_id=project_id
            )
            return redirect(reverse('accounting:settlements:detail', kwargs={'pk': settlement.pk}))
        except (ValueError, TypeError) as e:
            # Handle errors, e.g., invalid date format or no members in group
            # This is a simplified error handling
            pass

    groups = PartnersGroup.objects.all()
    projects = Project.objects.all()
    today = date.today()
    first_day_of_month = today.replace(day=1)

    context = {
        'groups': groups,
        'projects': projects,
        'default_from': first_day_of_month.strftime('%Y-%m-%d'),
        'default_to': today.strftime('%Y-%m-%d'),
        'page_title': 'إجراء تسوية جديدة'
    }
    return render(request, 'accounting/settlements/create.html', context)
