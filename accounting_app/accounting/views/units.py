"""
Unit Views with Advanced Features
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum
from decimal import Decimal

from accounting.models import Unit, UnitPartner, Partner, PartnersGroup
from accounting.services.returns import UnitReturnService
from accounting.services.audit import AuditService
from accounting.forms import UnitForm, UnitPartnerForm
from core.feature_flags import LEGACY_INLINE_EDITING_ENABLED


@login_required
def unit_list_view(request):
    """
    List all units with search and filters.
    """
    units = Unit.objects.all().select_related('partners_group')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        units = units.filter(
            Q(code__icontains=search) |
            Q(name__icontains=search) |
            Q(building_no__icontains=search)
        )
    
    # Filters
    unit_type = request.GET.get('type')
    if unit_type:
        units = units.filter(type=unit_type)
    
    status = request.GET.get('status')
    if status:
        units = units.filter(status=status)
    
    # Calculate remaining for each unit
    for unit in units:
        unit.remaining = unit.calculate_remaining()
        unit.partners_list = UnitPartner.objects.filter(
            unit=unit
        ).select_related('partner')
    
    context = {
        'units': units,
        'unit_types': Unit.UnitType.choices,
        'unit_statuses': [
            ('available', 'متاحة'),
            ('sold', 'مباعة'),
            ('reserved', 'محجوزة'),
            ('returned', 'مرتجعة'),
        ],
        'search': search,
        'selected_type': unit_type,
        'selected_status': status,
        'inline_editing_enabled': LEGACY_INLINE_EDITING_ENABLED,
    }
    
    return render(request, 'accounting/units/list.html', context)


@login_required
def unit_detail_view(request, pk):
    """
    Unit detail view with partner management.
    """
    unit = get_object_or_404(Unit, pk=pk)
    partners = UnitPartner.objects.filter(
        unit=unit
    ).select_related('partner')
    
    total_percent = sum(p.percent for p in partners)
    available_partners = Partner.objects.filter(is_active=True).exclude(
        id__in=partners.values_list('partner_id', flat=True)
    )
    
    # Check if unit can be sold
    can_create_contract = total_percent == 100 and unit.status == 'available'
    
    # Check if return process is available
    can_return = unit.status == 'sold' and hasattr(unit, 'contract')
    
    context = {
        'unit': unit,
        'partners': partners,
        'total_percent': total_percent,
        'available_partners': available_partners,
        'can_create_contract': can_create_contract,
        'can_return': can_return,
        'partner_return_enabled': LEGACY_PARTNER_RETURN_ENABLED,
    }
    
    return render(request, 'accounting/units/detail.html', context)


@login_required
@require_http_methods(["POST"])
def unit_add_partner(request, unit_id):
    """
    Add partner to unit (HTMX endpoint).
    """
    unit = get_object_or_404(Unit, pk=unit_id)
    
    partner_id = request.POST.get('partner_id')
    percent = request.POST.get('percent', 0)
    
    try:
        percent = Decimal(percent)
        if percent <= 0 or percent > 100:
            raise ValueError("النسبة يجب أن تكون بين 0 و 100")
        
        # Check total percentage
        current_total = UnitPartner.objects.filter(
            unit=unit
        ).aggregate(total=Sum('percent'))['total'] or 0
        
        if current_total + percent > 100:
            raise ValueError(f"لا يمكن إضافة هذه النسبة. الإجمالي الحالي: {current_total}%")
        
        partner = get_object_or_404(Partner, pk=partner_id)
        
        # Create unit partner
        unit_partner = UnitPartner.objects.create(
            unit=unit,
            partner=partner,
            percent=percent
        )
        
        # Log action
        AuditService.log_create(request.user, unit_partner, request)
        
        messages.success(request, f"تم إضافة {partner.name} بنسبة {percent}%")
        
    except Exception as e:
        messages.error(request, str(e))
    
    # Return updated partners list (HTMX partial)
    partners = UnitPartner.objects.filter(
        unit=unit
    ).select_related('partner')
    
    total_percent = sum(p.percent for p in partners)
    
    return render(request, 'accounting/units/partials/partners_list.html', {
        'unit': unit,
        'partners': partners,
        'total_percent': total_percent,
    })


@login_required
@require_http_methods(["POST"])
def unit_inline_edit(request, pk):
    """
    Inline edit unit field (HTMX endpoint).
    """
    if not LEGACY_INLINE_EDITING_ENABLED:
        return JsonResponse({'error': 'Inline editing is disabled'}, status=403)
    
    unit = get_object_or_404(Unit, pk=pk)
    field = request.POST.get('field')
    value = request.POST.get('value')
    
    allowed_fields = ['name', 'floor', 'area', 'notes']
    
    if field not in allowed_fields:
        return JsonResponse({'error': 'Field not allowed'}, status=400)
    
    try:
        old_value = getattr(unit, field)
        
        # Validate and set value
        if field == 'area' and value:
            value = Decimal(value)
        
        setattr(unit, field, value)
        unit.full_clean()
        unit.save()
        
        # Log change
        AuditService.log_update(
            request.user,
            unit,
            {field: {'old': old_value, 'new': value}},
            request
        )
        
        return JsonResponse({
            'success': True,
            'value': str(getattr(unit, field))
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def unit_return_preview(request, pk):
    """
    Preview unit return process.
    """
    unit = get_object_or_404(Unit, pk=pk)
    
    if request.method == 'POST':
        buying_partner_id = request.POST.get('buying_partner_id')
        
        try:
            preview = UnitReturnService.get_return_preview(
                unit, int(buying_partner_id)
            )
            
            if not preview['success']:
                messages.error(request, '; '.join(preview['errors']))
                return redirect('unit_detail', pk=unit.pk)
            
            return render(request, 'accounting/units/return_preview.html', preview)
            
        except Exception as e:
            messages.error(request, str(e))
            return redirect('unit_detail', pk=unit.pk)
    
    # GET request - show partner selection
    partners = UnitPartner.objects.filter(
        unit=unit
    ).select_related('partner')
    
    return render(request, 'accounting/units/return_select.html', {
        'unit': unit,
        'partners': partners,
    })


@login_required
@require_http_methods(["POST"])
def unit_return_execute(request, pk):
    """
    Execute unit return process.
    """
    unit = get_object_or_404(Unit, pk=pk)
    buying_partner_id = request.POST.get('buying_partner_id')
    
    try:
        service = UnitReturnService(unit, int(buying_partner_id))
        result = service.execute(user=request.user)
        
        messages.success(request, result['message'])
        return redirect('unit_detail', pk=unit.pk)
        
    except Exception as e:
        messages.error(request, str(e))
        return redirect('unit_detail', pk=unit.pk)


@login_required
def unit_create_view(request):
    """
    Create a new unit.
    """
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            unit = form.save()
            
            # Log creation
            AuditService.log_create(request.user, unit, request)
            
            messages.success(request, f'تم إنشاء الوحدة {unit.name} بنجاح')
            return redirect('units:unit_detail', pk=unit.pk)
    else:
        form = UnitForm()
    
    return render(request, 'accounting/units/form.html', {
        'form': form,
        'title': 'إضافة وحدة جديدة',
        'submit_text': 'إنشاء الوحدة'
    })


@login_required
def unit_edit_view(request, pk):
    """
    Edit unit details.
    """
    unit = get_object_or_404(Unit, pk=pk)
    
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            # Track changes
            old_values = {
                field: getattr(unit, field) 
                for field in form.changed_data
            }
            
            unit = form.save()
            
            # Log update
            changes = {
                field: {
                    'old': old_values[field],
                    'new': getattr(unit, field)
                }
                for field in form.changed_data
            }
            AuditService.log_update(request.user, unit, changes, request)
            
            messages.success(request, 'تم تحديث بيانات الوحدة بنجاح')
            return redirect('units:unit_detail', pk=unit.pk)
    else:
        form = UnitForm(instance=unit)
    
    return render(request, 'accounting/units/form.html', {
        'form': form,
        'unit': unit,
        'title': f'تعديل الوحدة: {unit.name}',
        'submit_text': 'حفظ التغييرات'
    })


@login_required
@require_http_methods(["POST"])
def unit_delete_view(request, pk):
    """
    Delete a unit.
    """
    unit = get_object_or_404(Unit, pk=pk)
    
    # Check if unit can be deleted
    if hasattr(unit, 'contract'):
        messages.error(request, 'لا يمكن حذف وحدة مرتبطة بعقد')
        return redirect('units:unit_detail', pk=unit.pk)
    
    # Check if unit has partners
    if UnitPartner.objects.filter(unit=unit).exists():
        messages.warning(request, 'يجب إزالة جميع الشركاء من الوحدة قبل الحذف')
        return redirect('units:unit_detail', pk=unit.pk)
    
    # Log deletion
    AuditService.log_delete(request.user, unit, request)
    
    unit_name = unit.name
    unit.delete()
    
    messages.success(request, f'تم حذف الوحدة {unit_name} بنجاح')
    return redirect('units:unit_list')