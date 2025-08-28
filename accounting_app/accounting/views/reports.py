"""
Advanced Reports Views
Professional reporting system with charts and export capabilities.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
import io

from accounting.models import (
    Unit, Contract, Customer, Partner, Installment,
    ReceiptVoucher, PaymentVoucher, UnitPartner, BrokerDue
)
from accounting.services.profits import PartnerProfitService
from accounting.services.import_export import ImportExportService


@login_required
def reports_home_view(request):
    """
    Reports dashboard with categories.
    """
    report_categories = {
        'financial': {
            'title': 'التقارير المالية',
            'icon': 'bi-graph-up',
            'color': 'primary',
            'reports': [
                {
                    'id': 'monthly_revenue',
                    'title': 'الإيرادات الشهرية',
                    'description': 'تحليل الإيرادات حسب الشهر مع المقارنات',
                    'icon': 'bi-calendar-month'
                },
                {
                    'id': 'cashflow',
                    'title': 'التدفقات النقدية',
                    'description': 'كشف تفصيلي بجميع الحركات المالية',
                    'icon': 'bi-cash-stack'
                },
                {
                    'id': 'expenses_analysis',
                    'title': 'تحليل المصروفات',
                    'description': 'تفصيل المصروفات حسب النوع والفترة',
                    'icon': 'bi-pie-chart'
                }
            ]
        },
        'partners': {
            'title': 'تقارير الشركاء',
            'icon': 'bi-people',
            'color': 'secondary',
            'reports': [
                {
                    'id': 'partner_profits',
                    'title': 'أرباح الشركاء',
                    'description': 'تفصيل الأرباح والخسائر لكل شريك',
                    'icon': 'bi-trophy'
                },
                {
                    'id': 'partner_ledger',
                    'title': 'كشف حساب شريك',
                    'description': 'كشف تفصيلي لحركات شريك محدد',
                    'icon': 'bi-journal-text'
                },
                {
                    'id': 'ownership_summary',
                    'title': 'ملخص الملكية',
                    'description': 'توزيع ملكية الوحدات على الشركاء',
                    'icon': 'bi-diagram-3'
                }
            ]
        },
        'operations': {
            'title': 'التقارير التشغيلية',
            'icon': 'bi-gear',
            'color': 'gold',
            'reports': [
                {
                    'id': 'overdue_installments',
                    'title': 'الأقساط المتأخرة',
                    'description': 'قائمة تفصيلية بالأقساط المتأخرة',
                    'icon': 'bi-exclamation-triangle'
                },
                {
                    'id': 'unit_status',
                    'title': 'حالة الوحدات',
                    'description': 'توزيع الوحدات حسب الحالة والنوع',
                    'icon': 'bi-building'
                },
                {
                    'id': 'broker_commissions',
                    'title': 'عمولات السماسرة',
                    'description': 'تقرير العمولات المستحقة والمدفوعة',
                    'icon': 'bi-person-badge'
                }
            ]
        }
    }
    
    context = {
        'report_categories': report_categories
    }
    
    return render(request, 'accounting/reports/home.html', context)


@login_required
def financial_reports_view(request):
    """
    Financial reports page with multiple report types.
    """
    # Get date range from request
    start_date = request.GET.get('start_date', timezone.now().date() - timedelta(days=30))
    end_date = request.GET.get('end_date', timezone.now().date())
    
    # Revenue analysis
    revenue_data = ReceiptVoucher.objects.filter(
        date__range=[start_date, end_date]
    ).aggregate(
        total=Sum('amount'),
        count=Count('id'),
        avg=Avg('amount')
    )
    
    # Expense analysis
    expense_data = PaymentVoucher.objects.filter(
        date__range=[start_date, end_date]
    ).aggregate(
        total=Sum('amount'),
        count=Count('id'),
        avg=Avg('amount')
    )
    
    # Monthly breakdown
    monthly_data = []
    current = datetime.strptime(str(start_date), '%Y-%m-%d')
    end = datetime.strptime(str(end_date), '%Y-%m-%d')
    
    while current <= end:
        month_revenue = ReceiptVoucher.objects.filter(
            date__year=current.year,
            date__month=current.month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_expense = PaymentVoucher.objects.filter(
            date__year=current.year,
            date__month=current.month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': current.strftime('%B %Y'),
            'revenue': float(month_revenue),
            'expense': float(month_expense),
            'profit': float(month_revenue - month_expense)
        })
        
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    context = {
        'revenue_data': revenue_data,
        'expense_data': expense_data,
        'monthly_data': monthly_data,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'accounting/reports/financial.html', context)


@login_required
def partner_reports_view(request):
    """
    Partner-specific reports.
    """
    partners = Partner.objects.all()
    
    # Partner profit analysis
    partner_data = []
    for partner in partners:
        profit_service = PartnerProfitService()
        profits = profit_service.calculate_partner_profit(partner.id)
        
        partner_data.append({
            'partner': partner,
            'total_profit': profits['total_profit'],
            'units_count': profits['units'].count(),
            'ownership_percentage': partner.share_percent
        })
    
    context = {
        'partner_data': partner_data
    }
    
    return render(request, 'accounting/reports/partners.html', context)


@login_required
def unit_reports_view(request):
    """
    Unit-specific reports.
    """
    # Unit status distribution
    status_data = Unit.objects.values('status').annotate(
        count=Count('id'),
        total_value=Sum('price')
    )
    
    # Unit type distribution
    type_data = Unit.objects.values('type').annotate(
        count=Count('id'),
        total_value=Sum('price')
    )
    
    # Partner ownership
    ownership_data = UnitPartner.objects.select_related(
        'unit', 'partner'
    ).values(
        'partner__name'
    ).annotate(
        units_count=Count('unit', distinct=True),
        total_percentage=Sum('percentage')
    )
    
    context = {
        'status_data': status_data,
        'type_data': type_data,
        'ownership_data': ownership_data
    }
    
    return render(request, 'accounting/reports/units.html', context)


@login_required
def overdue_report_view(request):
    """
    Overdue installments report.
    """
    today = timezone.now().date()
    
    overdue_installments = Installment.objects.filter(
        due_date__lt=today,
        status='PENDING'
    ).select_related(
        'contract__customer'
    ).order_by('due_date')
    
    # Group by customer
    customer_overdue = {}
    for installment in overdue_installments:
        customer = installment.contract.customer
        if customer.id not in customer_overdue:
            customer_overdue[customer.id] = {
                'customer': customer,
                'installments': [],
                'total_overdue': Decimal('0')
            }
        
        customer_overdue[customer.id]['installments'].append(installment)
        customer_overdue[customer.id]['total_overdue'] += installment.amount
    
    context = {
        'overdue_installments': overdue_installments,
        'customer_overdue': customer_overdue.values(),
        'total_overdue': sum(c['total_overdue'] for c in customer_overdue.values())
    }
    
    return render(request, 'accounting/reports/overdue.html', context)


@login_required
def cashflow_report_view(request):
    """
    Cash flow report.
    """
    # Get date range
    start_date = request.GET.get('start_date', timezone.now().date() - timedelta(days=30))
    end_date = request.GET.get('end_date', timezone.now().date())
    
    # Get all receipts
    receipts = ReceiptVoucher.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('safe', 'customer', 'contract').order_by('-date')
    
    # Get all payments
    payments = PaymentVoucher.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('safe', 'supplier').order_by('-date')
    
    # Calculate totals
    total_receipts = receipts.aggregate(total=Sum('amount'))['total'] or 0
    total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
    net_cashflow = total_receipts - total_payments
    
    context = {
        'receipts': receipts,
        'payments': payments,
        'total_receipts': total_receipts,
        'total_payments': total_payments,
        'net_cashflow': net_cashflow,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'accounting/reports/cashflow.html', context)


@login_required
def export_report_view(request, report_type):
    """
    Export reports to various formats.
    """
    format_type = request.GET.get('format', 'pdf')
    
    if report_type == 'financial':
        data = _get_financial_report_data(request)
    elif report_type == 'partners':
        data = _get_partner_report_data(request)
    elif report_type == 'units':
        data = _get_unit_report_data(request)
    elif report_type == 'overdue':
        data = _get_overdue_report_data(request)
    else:
        return HttpResponse('Invalid report type', status=400)
    
    # Export based on format
    if format_type == 'pdf':
        return ImportExportService.export_to_pdf(data, report_type)
    elif format_type == 'excel':
        return ImportExportService.export_to_excel(data, report_type)
    elif format_type == 'csv':
        return ImportExportService.export_to_csv(data, report_type)
    else:
        return HttpResponse('Invalid format type', status=400)


def _get_financial_report_data(request):
    """Helper to get financial report data."""
    # Implementation here
    return {}

def _get_partner_report_data(request):
    """Helper to get partner report data."""
    # Implementation here
    return {}

def _get_unit_report_data(request):
    """Helper to get unit report data."""
    # Implementation here
    return {}

def _get_overdue_report_data(request):
    """Helper to get overdue report data."""
    # Implementation here
    return {}