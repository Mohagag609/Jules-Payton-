"""
Fixed simple views
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


def error_response(title, error):
    """Return error page"""
    return HttpResponse(f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>خطأ</title>
        <meta charset="utf-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="alert alert-danger">
                <h4>{title}</h4>
                <p>{str(error)}</p>
                <hr>
                <a href="/accounting/" class="btn btn-primary">رجوع للرئيسية</a>
            </div>
        </div>
    </body>
    </html>
    """)


@login_required
def simple_units_list(request):
    """Simple units list"""
    try:
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
                        <a href="/admin/accounting/unit/add/" class="btn btn-primary mb-3">
                            <i class="bi bi-plus-circle me-1"></i>
                            إضافة وحدة جديدة
                        </a>
                        
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
            status = getattr(unit, 'status', 'available')
            status_class = {
                'available': 'success',
                'sold': 'danger',
                'reserved': 'warning',
                'returned': 'secondary'
            }.get(status, 'primary')
            
            html += f"""
                <tr>
                    <td>{unit.code}</td>
                    <td>{unit.name}</td>
                    <td>{getattr(unit, 'building_no', '-') or '-'}</td>
                    <td>{getattr(unit, 'type', '-')}</td>
                    <td><span class="badge bg-{status_class}">{status}</span></td>
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
    except Exception as e:
        return error_response("خطأ في صفحة الوحدات", e)


@login_required
def simple_contracts_list(request):
    """Simple contracts list"""
    try:
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
            remaining = contract.unit_value - contract.amount_paid
            html += f"""
                <tr>
                    <td>{contract.contract_no}</td>
                    <td>{contract.customer.name if contract.customer else '-'}</td>
                    <td>{contract.unit.name if contract.unit else '-'}</td>
                    <td>{contract.unit_value:,.2f} ج.م</td>
                    <td>{contract.amount_paid:,.2f} ج.م</td>
                    <td>{remaining:,.2f} ج.م</td>
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
    except Exception as e:
        return error_response("خطأ في صفحة العقود", e)


@login_required
def simple_partners_list(request):
    """Simple partners list"""
    try:
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
    except Exception as e:
        return error_response("خطأ في صفحة الشركاء", e)


@login_required
def simple_safes_list(request):
    """Simple safes list"""
    try:
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
    except Exception as e:
        return error_response("خطأ في صفحة الخزن", e)