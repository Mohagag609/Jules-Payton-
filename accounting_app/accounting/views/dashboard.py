from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta

from accounting.models import (
    ReceiptVoucher, PaymentVoucher, Customer, 
    Supplier, Project, Partner, Safe
)


@login_required
def dashboard_view(request):
    """Modern dashboard with comprehensive statistics"""
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    start_of_year = today.replace(month=1, day=1)
    
    # Calculate totals
    total_income = ReceiptVoucher.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    total_expenses = PaymentVoucher.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Project stats
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(active=True).count()
    
    # Customer stats
    total_customers = Customer.objects.count()
    new_customers = Customer.objects.filter(
        created_at__gte=start_of_month
    ).count()
    
    # Recent transactions
    recent_receipts = ReceiptVoucher.objects.select_related(
        'customer', 'safe'
    ).order_by('-date', '-id')[:5]
    
    recent_payments = PaymentVoucher.objects.select_related(
        'supplier', 'safe'
    ).order_by('-date', '-id')[:5]
    
    # Chart data (last 6 months)
    chart_data = []
    for i in range(6):
        month_start = (today - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        
        month_income = ReceiptVoucher.objects.filter(
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_expenses = PaymentVoucher.objects.filter(
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        chart_data.append({
            'month': month_start.strftime('%B'),
            'income': float(month_income),
            'expenses': float(month_expenses)
        })
    
    context = {
        'page_title': 'لوحة التحكم',
        'today': today,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_customers': total_customers,
        'new_customers': new_customers,
        'recent_receipts': recent_receipts,
        'recent_payments': recent_payments,
        'chart_data': chart_data,
    }
    
    return render(request, 'accounting/modern_dashboard.html', context)