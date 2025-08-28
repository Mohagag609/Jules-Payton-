"""
Luxury Dashboard Views
Professional real estate management dashboard with advanced analytics.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from decimal import Decimal
import json

from accounting.models import (
    Unit, Contract, Customer, Partner, Installment,
    Safe, ReceiptVoucher, PaymentVoucher, BrokerDue
)
from core.feature_flags import LEGACY_UNDO_REDO_ENABLED


@login_required
def dashboard_view(request):
    """
    Main dashboard with KPIs and charts.
    """
    try:
        # Date filters
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        
        # Calculate KPIs
        kpis = calculate_kpis(from_date, to_date)
        
        # Get upcoming installments
        upcoming_installments = get_upcoming_installments()
        
        # Get recent transactions
        recent_transactions = get_recent_transactions()
    except Exception as e:
        # Log error and return safe defaults
        print(f"Dashboard error: {str(e)}")
        kpis = {
            'financial': {'total_revenue': 0, 'total_expenses': 0, 'net_profit': 0, 'pending_payments': 0},
            'units': {'total': 0, 'available': 0, 'sold': 0, 'reserved': 0, 'returned': 0},
            'contracts': {'total': 0, 'active': 0, 'completed': 0, 'installments_total': 0},
            'customers': {'total': 0, 'active': 0, 'new_this_month': 0}
        }
        upcoming_installments = []
        recent_transactions = []
    
    # Unit status chart data
    unit_chart_data = {
        'labels': ['متاحة', 'مباعة', 'محجوزة', 'مرتجعة'],
        'data': [
            kpis['units']['available'],
            kpis['units']['sold'],
            kpis['units']['reserved'],
            kpis['units']['returned']
        ],
        'colors': ['#2563eb', '#16a34a', '#f59e0b', '#ef4444']
    }
    
    # Monthly revenue chart
    monthly_revenue = get_monthly_revenue_data()
    
    # Partner profits summary
    partner_profits = get_partner_profits_summary()
    
    context = {
        'kpis': kpis,
        'upcoming_installments': upcoming_installments,
        'recent_transactions': recent_transactions,
        'unit_chart_data': json.dumps(unit_chart_data),
        'monthly_revenue_data': json.dumps(monthly_revenue),
        'partner_profits': partner_profits,
        'from_date': from_date,
        'to_date': to_date,
    }
    
    return render(request, 'accounting/dashboard.html', context)


def calculate_kpis(from_date=None, to_date=None):
    """
    Calculate Key Performance Indicators.
    """
    # Date filtering
    date_filter = Q()
    if from_date:
        date_filter &= Q(created_at__gte=from_date)
    if to_date:
        date_filter &= Q(created_at__lte=to_date)
    
    # Units KPIs
    units = {
        'total': Unit.objects.count(),
        'available': Unit.objects.filter(status='available').count(),
        'sold': Unit.objects.filter(status='sold').count(),
        'reserved': Unit.objects.filter(status='reserved').count(),
        'returned': Unit.objects.filter(status='returned').count(),
    }
    
    # Financial KPIs
    contracts = Contract.objects.filter(date_filter)
    total_sales = contracts.aggregate(
        total=Sum('unit_value')
    )['total'] or Decimal('0')
    
    # Total receipts
    receipts = ReceiptVoucher.objects.filter(date_filter)
    total_receipts = receipts.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    # Total payments
    payments = PaymentVoucher.objects.filter(date_filter)
    total_payments = payments.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    # Total debt (remaining installments)
    total_debt = Installment.objects.filter(
        status__in=['PENDING', 'LATE', 'PARTIAL']
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    # Collection percentage
    collection_percentage = 0
    if total_sales > 0:
        collection_percentage = (total_receipts / total_sales * 100).quantize(Decimal('0.01'))
    
    # Net profit
    net_profit = total_receipts - total_payments
    
    # Customer statistics
    customers = {
        'total': Customer.objects.count(),
        'active': Customer.objects.filter(status='active').count(),
        'new_this_month': Customer.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count(),
    }
    
    # Partner statistics
    partners = {
        'total': Partner.objects.count(),
        'active': Partner.objects.filter(is_active=True).count(),
    }
    
    # Broker commissions
    broker_commissions = {
        'due': BrokerDue.objects.filter(status='due').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0'),
        'paid': BrokerDue.objects.filter(status='paid').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0'),
    }
    
    return {
        'units': units,
        'financial': {
            'total_sales': total_sales,
            'total_receipts': total_receipts,
            'total_payments': total_payments,
            'total_debt': total_debt,
            'collection_percentage': collection_percentage,
            'net_profit': net_profit,
        },
        'customers': customers,
        'partners': partners,
        'broker_commissions': broker_commissions,
    }


def get_upcoming_installments(limit=10):
    """
    Get upcoming installments that are due.
    """
    today = timezone.now().date()
    
    installments = Installment.objects.filter(
        status__in=['PENDING', 'LATE', 'PARTIAL'],
        due_date__gte=today - timedelta(days=7)  # Include recently overdue
    ).select_related(
        'contract__customer',
        'contract__unit'
    ).order_by('due_date')[:limit]
    
    data = []
    for inst in installments:
        days_until_due = (inst.due_date - today).days
        status_class = 'warning'
        if days_until_due < 0:
            status_class = 'danger'
        elif days_until_due > 7:
            status_class = 'info'
        
        data.append({
            'id': inst.id,
            'unit': inst.contract.unit.name,
            'customer': inst.contract.customer.name,
            'amount': inst.amount,
            'due_date': inst.due_date,
            'days_until_due': days_until_due,
            'status': inst.status,
            'status_class': status_class,
        })
    
    return data


def get_recent_transactions(limit=10):
    """
    Get recent financial transactions.
    """
    # Get recent receipts
    receipts = list(ReceiptVoucher.objects.select_related('safe').order_by('-voucher_date')[:limit])
    
    # Get recent payments
    payments = list(PaymentVoucher.objects.select_related('safe').order_by('-voucher_date')[:limit])
    
    # Combine and sort
    transactions = []
    
    for receipt in receipts:
        transactions.append({
            'type': 'receipt',
            'type_display': 'قبض',
            'date': receipt.voucher_date,
            'amount': receipt.amount,
            'description': receipt.description,
            'safe': receipt.safe.name,
            'reference': receipt.voucher_no,
            'icon': 'bi-arrow-down-circle-fill',
            'color': 'success',
        })
    
    for payment in payments:
        transactions.append({
            'type': 'payment',
            'type_display': 'صرف',
            'date': payment.voucher_date,
            'amount': payment.amount,
            'description': payment.description,
            'safe': payment.safe.name,
            'reference': payment.voucher_no,
            'icon': 'bi-arrow-up-circle-fill',
            'color': 'danger',
        })
    
    # Sort by date descending
    transactions.sort(key=lambda x: x['date'], reverse=True)
    
    return transactions[:limit]


def get_monthly_revenue_data():
    """
    Get monthly revenue data for the last 12 months.
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    # Get monthly receipts
    receipts = ReceiptVoucher.objects.filter(
        voucher_date__gte=start_date,
        voucher_date__lte=end_date
    ).values(
        'voucher_date__year',
        'voucher_date__month'
    ).annotate(
        total=Sum('amount')
    ).order_by('voucher_date__year', 'voucher_date__month')
    
    # Format data for Chart.js
    labels = []
    data = []
    
    for receipt in receipts:
        year = receipt['voucher_date__year']
        month = receipt['voucher_date__month']
        labels.append(f"{month}/{year}")
        data.append(float(receipt['total']))
    
    return {
        'labels': labels,
        'datasets': [{
            'label': 'الإيرادات الشهرية',
            'data': data,
            'backgroundColor': 'rgba(30, 58, 138, 0.1)',
            'borderColor': 'rgba(30, 58, 138, 1)',
            'borderWidth': 2,
            'tension': 0.4,
        }]
    }


def get_partner_profits_summary():
    """
    Get summary of partner profits.
    """
    from accounting.models import UnitPartner
    
    partners = Partner.objects.filter(is_active=True)
    
    summary = []
    for partner in partners:
        # Get units owned by this partner
        unit_partnerships = UnitPartner.objects.filter(
            partner=partner
        ).select_related('unit')
        
        total_share_value = Decimal('0')
        total_receipts = Decimal('0')
        
        for partnership in unit_partnerships:
            # Calculate share value
            share_value = (partnership.unit.price_total * partnership.percent / 100)
            total_share_value += share_value
            
            # Calculate receipts share
            contract = Contract.objects.filter(unit=partnership.unit).first()
            if contract:
                receipts = ReceiptVoucher.objects.filter(
                    reference_id=contract.id,
                    voucher_type='contract_payment'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                partner_receipts = (receipts * partnership.percent / 100)
                total_receipts += partner_receipts
        
        if total_share_value > 0:
            summary.append({
                'partner': partner,
                'total_units': unit_partnerships.count(),
                'total_share_value': total_share_value,
                'total_receipts': total_receipts,
                'profit_percentage': (total_receipts / total_share_value * 100).quantize(Decimal('0.01'))
            })
    
    # Sort by total receipts descending
    summary.sort(key=lambda x: x['total_receipts'], reverse=True)
    
    return summary[:5]  # Top 5 partners


@login_required
@require_http_methods(["POST"])
def undo_action(request):
    """
    Undo last action (AJAX endpoint).
    """
    if not LEGACY_UNDO_REDO_ENABLED:
        return JsonResponse({'error': 'Undo/Redo is disabled'}, status=403)
    
    undo_stack = request.session.get('undo_stack', [])
    undo_index = request.session.get('undo_index', -1)
    
    if undo_index > 0:
        undo_index -= 1
        request.session['undo_index'] = undo_index
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'تم التراجع بنجاح',
            'can_undo': undo_index > 0,
            'can_redo': True
        })
    
    return JsonResponse({
        'success': False,
        'message': 'لا يمكن التراجع أكثر'
    })


@login_required
@require_http_methods(["POST"])
def redo_action(request):
    """
    Redo action (AJAX endpoint).
    """
    if not LEGACY_UNDO_REDO_ENABLED:
        return JsonResponse({'error': 'Undo/Redo is disabled'}, status=403)
    
    undo_stack = request.session.get('undo_stack', [])
    undo_index = request.session.get('undo_index', -1)
    
    if undo_index < len(undo_stack) - 1:
        undo_index += 1
        request.session['undo_index'] = undo_index
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'تمت الإعادة بنجاح',
            'can_undo': True,
            'can_redo': undo_index < len(undo_stack) - 1
        })
    
    return JsonResponse({
        'success': False,
        'message': 'لا يمكن الإعادة أكثر'
    })


@login_required
@require_http_methods(["POST"])
def update_theme(request):
    """
    Update user theme preference (AJAX endpoint).
    """
    import json
    
    try:
        data = json.loads(request.body)
        theme = data.get('theme', 'dark')
        
        if hasattr(request.user, 'settings'):
            settings = request.user.settings
            settings.theme = theme
            settings.save()
        else:
            from accounting.models import UserSettings
            UserSettings.objects.create(
                user=request.user,
                theme=theme
            )
        
        return JsonResponse({
            'success': True,
            'theme': theme
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def global_search(request):
    """
    Global search across all models (AJAX endpoint).
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    
    # Search units
    units = Unit.objects.filter(
        Q(code__icontains=query) |
        Q(name__icontains=query)
    )[:5]
    
    for unit in units:
        results.append({
            'type': 'unit',
            'title': unit.name,
            'subtitle': f'كود: {unit.code}',
            'url': f'/units/{unit.id}/',
            'icon': 'bi-building'
        })
    
    # Search customers
    customers = Customer.objects.filter(
        Q(name__icontains=query) |
        Q(phone__icontains=query) |
        Q(code__icontains=query)
    )[:5]
    
    for customer in customers:
        results.append({
            'type': 'customer',
            'title': customer.name,
            'subtitle': f'هاتف: {customer.phone}',
            'url': f'/customers/{customer.id}/',
            'icon': 'bi-person'
        })
    
    # Search contracts
    contracts = Contract.objects.filter(
        Q(code__icontains=query)
    ).select_related('customer', 'unit')[:5]
    
    for contract in contracts:
        results.append({
            'type': 'contract',
            'title': f'عقد {contract.code}',
            'subtitle': f'{contract.customer.name} - {contract.unit.name}',
            'url': f'/contracts/{contract.id}/',
            'icon': 'bi-file-text'
        })
    
    return render(request, 'partials/search_results.html', {
        'results': results[:10]  # Limit to 10 results
    })


@login_required
@require_http_methods(["POST"])
def lock_app(request):
    """
    Lock the application.
    """
    if hasattr(request.user, 'settings'):
        settings = request.user.settings
        settings.is_locked = True
        settings.save()
        
        request.session['unlocked'] = False
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)


@login_required
@require_http_methods(["POST"])
def unlock_app(request):
    """
    Unlock the application.
    """
    password = request.POST.get('password')
    
    if hasattr(request.user, 'settings'):
        settings = request.user.settings
        
        if settings.lock_password == password:
            request.session['unlocked'] = True
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False,
                'error': 'كلمة المرور غير صحيحة'
            }, status=400)
    
    return JsonResponse({'success': False}, status=400)


@login_required
def dashboard_export_view(request):
    """
    Export dashboard data to Excel.
    """
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Calculate KPIs
    kpis = calculate_kpis(from_date, to_date)
    
    # Prepare data for export
    data_dict = {
        'المؤشرات الرئيسية': {
            'model_name': 'custom',
            'data': [{
                'المؤشر': 'إجمالي المبيعات',
                'القيمة': float(kpis['financial']['total_sales'])
            }, {
                'المؤشر': 'إجمالي المتحصلات',
                'القيمة': float(kpis['financial']['total_receipts'])
            }, {
                'المؤشر': 'إجمالي المديونية',
                'القيمة': float(kpis['financial']['total_debt'])
            }, {
                'المؤشر': 'صافي الربح',
                'القيمة': float(kpis['financial']['net_profit'])
            }]
        },
        'حالة الوحدات': {
            'model_name': 'custom',
            'data': [{
                'الحالة': 'متاحة',
                'العدد': kpis['units']['available']
            }, {
                'الحالة': 'مباعة',
                'العدد': kpis['units']['sold']
            }, {
                'الحالة': 'محجوزة',
                'العدد': kpis['units']['reserved']
            }]
        }
    }
    
    # Generate Excel
    from accounting.services.import_export import ImportExportService
    excel_data = ImportExportService.export_excel(
        data_dict,
        filename=f'dashboard_{timezone.now().date()}.xlsx',
        user=request.user
    )
    
    response = HttpResponse(
        excel_data,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="dashboard.xlsx"'
    
    return response


@login_required
def dashboard_print_view(request):
    """
    Print-friendly dashboard view.
    """
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Calculate KPIs
    kpis = calculate_kpis(from_date, to_date)
    
    # Get data
    upcoming_installments = get_upcoming_installments(20)  # More for print
    recent_transactions = get_recent_transactions(20)
    partner_profits = get_partner_profits_summary()
    
    context = {
        'kpis': kpis,
        'upcoming_installments': upcoming_installments,
        'recent_transactions': recent_transactions,
        'partner_profits': partner_profits,
        'from_date': from_date,
        'to_date': to_date,
        'print_mode': True
    }
    
    return render(request, 'accounting/dashboard_print.html', context)