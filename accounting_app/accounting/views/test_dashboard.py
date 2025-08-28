"""
Test dashboard view
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required
def simple_dashboard_view(request):
    """Simple test dashboard"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>لوحة التحكم - اختبار</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .info {
                background: #e3f2fd;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .links {
                text-align: center;
                margin-top: 30px;
            }
            .links a {
                display: inline-block;
                padding: 10px 20px;
                background: #2196f3;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 0 10px;
            }
            .links a:hover {
                background: #1976d2;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>مرحباً في لوحة التحكم</h1>
            <div class="info">
                <p><strong>المستخدم:</strong> """ + request.user.username + """</p>
                <p><strong>البريد الإلكتروني:</strong> """ + request.user.email + """</p>
                <p>لوحة التحكم تعمل بنجاح! ✅</p>
            </div>
            <div class="links">
                <a href="/admin/">لوحة الإدارة</a>
                <a href="/accounting/units/">الوحدات</a>
                <a href="/accounting/contracts/">العقود</a>
                <a href="/accounting/customers/">العملاء</a>
            </div>
        </div>
    </body>
    </html>
    """)


@login_required
def test_dashboard_data(request):
    """Test database access"""
    try:
        from accounting.models import Unit, Customer, Contract, Partner
        
        data = {
            'units': Unit.objects.count(),
            'customers': Customer.objects.count(),
            'contracts': Contract.objects.count(),
            'partners': Partner.objects.count(),
        }
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <title>اختبار البيانات</title>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>إحصائيات قاعدة البيانات</h1>
            <ul>
                <li>عدد الوحدات: {data['units']}</li>
                <li>عدد العملاء: {data['customers']}</li>
                <li>عدد العقود: {data['contracts']}</li>
                <li>عدد الشركاء: {data['partners']}</li>
            </ul>
            <p style="color: green;">✅ قاعدة البيانات تعمل بنجاح!</p>
        </body>
        </html>
        """
        return HttpResponse(html)
        
    except Exception as e:
        return HttpResponse(f"""
        <html dir="rtl">
        <body style="font-family: Arial; padding: 20px;">
            <h1 style="color: red;">خطأ في قاعدة البيانات</h1>
            <pre>{str(e)}</pre>
        </body>
        </html>
        """)