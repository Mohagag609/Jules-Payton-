"""
Simple views to replace complex ones temporarily
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count

from accounting.models import (
    Unit, Contract, Customer, Partner, Installment,
    Safe, ReceiptVoucher, PaymentVoucher
)


@login_required
def simple_dashboard(request):
    """Simple dashboard without complex calculations"""
    context = {
        'units_count': Unit.objects.count(),
        'customers_count': Customer.objects.count(),
        'contracts_count': Contract.objects.count(),
        'partners_count': Partner.objects.count(),
        'total_revenue': ReceiptVoucher.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'total_expenses': PaymentVoucher.objects.aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    # Simple HTML dashboard
    return HttpResponse(f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>لوحة التحكم</title>
        <meta charset="utf-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
        <style>
            body {{
                background: #f8f9fa;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            .dashboard-card {{
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
                transition: transform 0.2s;
            }}
            .dashboard-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
            }}
            .stat-number {{
                font-size: 2.5rem;
                font-weight: bold;
                color: #2196f3;
            }}
            .navbar {{
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">
                    <i class="bi bi-building me-2"></i>
                    نظام إدارة العقارات
                </a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/admin/">
                        <i class="bi bi-gear me-1"></i>
                        لوحة الإدارة
                    </a>
                    <a class="nav-link" href="/admin/logout/">
                        <i class="bi bi-box-arrow-right me-1"></i>
                        تسجيل خروج
                    </a>
                </div>
            </div>
        </nav>
        
        <div class="container">
            <h1 class="text-center mb-5">لوحة التحكم الرئيسية</h1>
            
            <div class="row">
                <div class="col-md-3">
                    <div class="dashboard-card text-center">
                        <i class="bi bi-building text-primary" style="font-size: 3rem;"></i>
                        <h5 class="mt-3">الوحدات</h5>
                        <div class="stat-number">{context['units_count']}</div>
                        <a href="/accounting/units/" class="btn btn-sm btn-primary mt-2">عرض الكل</a>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="dashboard-card text-center">
                        <i class="bi bi-people text-success" style="font-size: 3rem;"></i>
                        <h5 class="mt-3">العملاء</h5>
                        <div class="stat-number">{context['customers_count']}</div>
                        <a href="/accounting/customers/" class="btn btn-sm btn-success mt-2">عرض الكل</a>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="dashboard-card text-center">
                        <i class="bi bi-file-text text-info" style="font-size: 3rem;"></i>
                        <h5 class="mt-3">العقود</h5>
                        <div class="stat-number">{context['contracts_count']}</div>
                        <a href="/accounting/contracts/" class="btn btn-sm btn-info mt-2">عرض الكل</a>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="dashboard-card text-center">
                        <i class="bi bi-person-badge text-warning" style="font-size: 3rem;"></i>
                        <h5 class="mt-3">الشركاء</h5>
                        <div class="stat-number">{context['partners_count']}</div>
                        <a href="/accounting/partners/" class="btn btn-sm btn-warning mt-2">عرض الكل</a>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="dashboard-card">
                        <h5>
                            <i class="bi bi-cash-stack text-success me-2"></i>
                            الإيرادات
                        </h5>
                        <div class="stat-number text-success">
                            {context['total_revenue']:,.2f} ج.م
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="dashboard-card">
                        <h5>
                            <i class="bi bi-receipt text-danger me-2"></i>
                            المصروفات
                        </h5>
                        <div class="stat-number text-danger">
                            {context['total_expenses']:,.2f} ج.م
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="dashboard-card">
                        <h5 class="mb-3">روابط سريعة</h5>
                        <div class="d-flex flex-wrap gap-2">
                            <a href="/accounting/units/" class="btn btn-outline-primary">
                                <i class="bi bi-building me-1"></i>
                                الوحدات
                            </a>
                            <a href="/accounting/customers/" class="btn btn-outline-success">
                                <i class="bi bi-people me-1"></i>
                                العملاء
                            </a>
                            <a href="/accounting/contracts/" class="btn btn-outline-info">
                                <i class="bi bi-file-text me-1"></i>
                                العقود
                            </a>
                            <a href="/accounting/partners/" class="btn btn-outline-warning">
                                <i class="bi bi-person-badge me-1"></i>
                                الشركاء
                            </a>
                            <a href="/accounting/safes/" class="btn btn-outline-dark">
                                <i class="bi bi-safe me-1"></i>
                                الخزن
                            </a>
                            <a href="/accounting/reports/" class="btn btn-outline-secondary">
                                <i class="bi bi-graph-up me-1"></i>
                                التقارير
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """)


@login_required
def simple_units_list(request):
    """Simple units list"""
    units = Unit.objects.all()
    
    html = """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>قائمة الوحدات</title>
        <meta charset="utf-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="/accounting/">
                    <i class="bi bi-arrow-right me-2"></i>
                    رجوع للرئيسية
                </a>
            </div>
        </nav>
        
        <div class="container">
            <h1 class="mb-4">قائمة الوحدات</h1>
            
            <div class="card">
                <div class="card-body">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>الكود</th>
                                <th>الاسم</th>
                                <th>رقم المبنى</th>
                                <th>النوع</th>
                                <th>الحالة</th>
                                <th>السعر</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for unit in units:
        status_class = {
            'available': 'success',
            'sold': 'danger',
            'reserved': 'warning',
            'returned': 'secondary'
        }.get(unit.status, 'primary')
        
        html += f"""
            <tr>
                <td>{unit.code}</td>
                <td>{unit.name}</td>
                <td>{unit.building_no or '-'}</td>
                <td>{unit.get_type_display() if hasattr(unit, 'get_type_display') else unit.type}</td>
                <td><span class="badge bg-{status_class}">{unit.get_status_display() if hasattr(unit, 'get_status_display') else unit.status}</span></td>
                <td>{unit.price_total:,.2f} ج.م</td>
            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return HttpResponse(html)


@login_required
def simple_customers_list(request):
    """Simple customers list"""
    customers = Customer.objects.all()
    
    html = """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>قائمة العملاء</title>
        <meta charset="utf-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="/accounting/">
                    <i class="bi bi-arrow-right me-2"></i>
                    رجوع للرئيسية
                </a>
            </div>
        </nav>
        
        <div class="container">
            <h1 class="mb-4">قائمة العملاء</h1>
            
            <div class="card">
                <div class="card-body">
                    <a href="/admin/accounting/customer/add/" class="btn btn-primary mb-3">
                        <i class="bi bi-plus-circle me-1"></i>
                        إضافة عميل جديد
                    </a>
                    
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>الكود</th>
                                <th>الاسم</th>
                                <th>الهاتف</th>
                                <th>البريد الإلكتروني</th>
                                <th>الحالة</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for customer in customers:
        html += f"""
            <tr>
                <td>{customer.code}</td>
                <td>{customer.name}</td>
                <td>{customer.phone or '-'}</td>
                <td>{customer.email or '-'}</td>
                <td><span class="badge bg-success">نشط</span></td>
            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return HttpResponse(html)


@login_required
def simple_contracts_list(request):
    """Simple contracts list"""
    contracts = Contract.objects.all().select_related('customer', 'unit')
    
    html = """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>قائمة العقود</title>
        <meta charset="utf-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="/accounting/">
                    <i class="bi bi-arrow-right me-2"></i>
                    رجوع للرئيسية
                </a>
            </div>
        </nav>
        
        <div class="container">
            <h1 class="mb-4">قائمة العقود</h1>
            
            <div class="card">
                <div class="card-body">
                    <a href="/admin/accounting/contract/add/" class="btn btn-primary mb-3">
                        <i class="bi bi-plus-circle me-1"></i>
                        إضافة عقد جديد
                    </a>
                    
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>رقم العقد</th>
                                <th>العميل</th>
                                <th>الوحدة</th>
                                <th>القيمة الإجمالية</th>
                                <th>المدفوع</th>
                                <th>المتبقي</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for contract in contracts:
        html += f"""
            <tr>
                <td>{contract.contract_no}</td>
                <td>{contract.customer.name if contract.customer else '-'}</td>
                <td>{contract.unit.name if contract.unit else '-'}</td>
                <td>{contract.unit_value:,.2f} ج.م</td>
                <td>{contract.amount_paid:,.2f} ج.م</td>
                <td>{contract.remaining_amount:,.2f} ج.م</td>
            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return HttpResponse(html)


@login_required
def simple_partners_list(request):
    """Simple partners list"""
    partners = Partner.objects.all()
    
    html = """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>قائمة الشركاء</title>
        <meta charset="utf-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="/accounting/">
                    <i class="bi bi-arrow-right me-2"></i>
                    رجوع للرئيسية
                </a>
            </div>
        </nav>
        
        <div class="container">
            <h1 class="mb-4">قائمة الشركاء</h1>
            
            <div class="card">
                <div class="card-body">
                    <a href="/admin/accounting/partner/add/" class="btn btn-primary mb-3">
                        <i class="bi bi-plus-circle me-1"></i>
                        إضافة شريك جديد
                    </a>
                    
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>الكود</th>
                                <th>الاسم</th>
                                <th>نسبة الحصة</th>
                                <th>الرصيد الافتتاحي</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for partner in partners:
        html += f"""
            <tr>
                <td>{partner.code}</td>
                <td>{partner.name}</td>
                <td>{partner.share_percent}%</td>
                <td>{partner.opening_balance:,.2f} ج.م</td>
            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return HttpResponse(html)


@login_required
def simple_safes_list(request):
    """Simple safes list"""
    safes = Safe.objects.all()
    
    html = """
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>قائمة الخزن</title>
        <meta charset="utf-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="/accounting/">
                    <i class="bi bi-arrow-right me-2"></i>
                    رجوع للرئيسية
                </a>
            </div>
        </nav>
        
        <div class="container">
            <h1 class="mb-4">قائمة الخزن</h1>
            
            <div class="card">
                <div class="card-body">
                    <a href="/admin/accounting/safe/add/" class="btn btn-primary mb-3">
                        <i class="bi bi-plus-circle me-1"></i>
                        إضافة خزنة جديدة
                    </a>
                    
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>الكود</th>
                                <th>الاسم</th>
                                <th>الرصيد الحالي</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for safe in safes:
        html += f"""
            <tr>
                <td>{safe.code}</td>
                <td>{safe.name}</td>
                <td>{safe.balance:,.2f} ج.م</td>
            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    return HttpResponse(html)