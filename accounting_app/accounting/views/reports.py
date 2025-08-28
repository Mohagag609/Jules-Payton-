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