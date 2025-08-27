import csv
from datetime import date, timedelta
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

from accounting.models import Safe, Customer, Partner, Project, Supplier
from accounting.services.reports import (
    get_treasury_report_data, get_installments_report_data,
    get_partner_balances_report_data, get_expenses_report_data
)

@login_required
def report_index_view(request):
    """
    Shows the main page for selecting a report.
    """
    safes = Safe.objects.all()
    customers = Customer.objects.all()
    projects = Project.objects.all()
    suppliers = Supplier.objects.all()
    today = date.today()
    first_day_of_month = today.replace(day=1)

    context = {
        'page_title': 'التقارير',
        'safes': safes,
        'customers': customers,
        'projects': projects,
        'suppliers': suppliers,
        'default_from': first_day_of_month.strftime('%Y-%m-%d'),
        'default_to': today.strftime('%Y-%m-%d'),
    }
    return render(request, 'accounting/reports/index.html', context)

@login_required
def treasury_report_view(request):
    """
    Generates and downloads the Treasury Report as either HTML, CSV, or PDF.
    """
    # Get parameters
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    safe_id = request.GET.get('safe')
    output_format = request.GET.get('format', 'html')

    # Basic validation and conversion
    try:
        from_date = date.fromisoformat(from_date_str)
        to_date = date.fromisoformat(to_date_str)
    except (ValueError, TypeError):
        # Handle error appropriately
        return HttpResponse("تنسيق التاريخ غير صالح.", status=400)

    safe = None
    if safe_id:
        safe = Safe.objects.filter(pk=safe_id).first()

    # Get data from the service
    report_data = get_treasury_report_data(from_date, to_date, safe)

    context = {
        'report_data': report_data,
        'from_date': from_date,
        'to_date': to_date,
        'selected_safe': safe,
    }

    if output_format == 'pdf':
        from weasyprint import HTML, CSS
        # Render HTML template to a string
        html_string = render_to_string('accounting/reports/treasury_pdf.html', context)
        # WeasyPrint needs a base URL to resolve relative paths for CSS, etc.
        base_url = request.build_absolute_uri('/')
        # A simple CSS for RTL PDF
        pdf_css = CSS(string='''
            @page { size: A4; margin: 2cm; }
            body { font-family: 'Cairo', sans-serif; direction: rtl; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
            th { background-color: #f2f2f2; }
        ''')
        pdf_file = HTML(string=html_string, base_url=base_url).write_pdf(stylesheets=[pdf_css])

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="treasury_report.pdf"'
        return response

    elif output_format == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="treasury_report.csv"'
        response.write('\ufeff'.encode('utf8')) # BOM for Excel

        writer = csv.writer(response)
        # Write header
        writer.writerow(['الخزنة', 'تاريخ', 'البيان', 'وارد', 'منصرف'])

        for data in report_data:
            writer.writerow([data['safe'].name, '', 'رصيد افتتاحي', data['opening_balance'], ''])
            for tx in data['transactions']:
                is_receipt = isinstance(tx, ReceiptVoucher)
                writer.writerow([
                    data['safe'].name,
                    tx.date,
                    tx.description,
                    tx.amount if is_receipt else '',
                    tx.amount if not is_receipt else '',
                ])
            writer.writerow([data['safe'].name, '', 'رصيد ختامي', '', data['closing_balance']])

        return response

    # Default to HTML view
    return render(request, 'accounting/reports/treasury_report_view.html', context)


@login_required
def installments_report_view(request):
    """
    Generates and downloads the Installments Report.
    """
    customer_id = request.GET.get('customer')
    status = request.GET.get('status')
    output_format = request.GET.get('format', 'html')

    customer = None
    if customer_id:
        customer = Customer.objects.filter(pk=customer_id).first()

    report_data = get_installments_report_data(customer=customer, status=status)

    context = {
        'report_data': report_data,
        'selected_customer': customer,
        'selected_status': status,
    }

    if output_format == 'pdf':
        from weasyprint import HTML, CSS
        html_string = render_to_string('accounting/reports/installments_pdf.html', context)
        base_url = request.build_absolute_uri('/')
        pdf_css = CSS(string='''
            @page { size: A4; margin: 2cm; }
            body { font-family: 'Cairo', sans-serif; direction: rtl; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
            th { background-color: #f2f2f2; }
            .total-row { font-weight: bold; background-color: #e8e8e8; }
        ''')
        pdf_file = HTML(string=html_string, base_url=base_url).write_pdf(stylesheets=[pdf_css])

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="installments_report.pdf"'
        return response

    elif output_format == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="installments_report.csv"'
        response.write('\ufeff'.encode('utf8'))

        writer = csv.writer(response)
        writer.writerow(['العقد', 'العميل', 'رقم القسط', 'تاريخ الاستحقاق', 'المبلغ', 'المدفوع', 'المتبقي', 'الحالة'])

        for inst in report_data['installments']:
            writer.writerow([
                inst.contract.code,
                inst.contract.customer.name,
                inst.seq_no,
                inst.due_date,
                inst.amount,
                inst.paid_amount,
                inst.remaining_amount,
                inst.get_status_display(),
            ])

        totals = report_data['totals']
        writer.writerow(['الإجمالي', '', '', '', totals['total_amount'], totals['total_paid'], totals['total_remaining'], ''])

        return response

    # Default to HTML view
    return render(request, 'accounting/reports/installments_report_view.html', context)


@login_required
def partner_balances_report_view(request):
    """
    Generates and downloads the Partner Balances Report.
    """
    report_data = get_partner_balances_report_data()
    context = {'report_data': report_data}

    # This is a simple report, so we'll just implement HTML and CSV for now.
    output_format = request.GET.get('format', 'html')

    if output_format == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="partner_balances.csv"'
        response.write('\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        writer.writerow(['الشريك', 'المحفظة', 'الرصيد الحالي'])
        for row in report_data:
            writer.writerow([row['partner_name'], row['wallet_name'], row['balance']])
        return response

    return render(request, 'accounting/reports/partner_balances_report_view.html', context)


@login_required
def expenses_report_view(request):
    """
    Generates and downloads the Expenses Report.
    """
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    project_id = request.GET.get('project')
    supplier_id = request.GET.get('supplier')
    output_format = request.GET.get('format', 'html')

    try:
        from_date = date.fromisoformat(from_date_str)
        to_date = date.fromisoformat(to_date_str)
    except (ValueError, TypeError):
        return HttpResponse("تنسيق التاريخ غير صالح.", status=400)

    project = Project.objects.filter(pk=project_id).first() if project_id else None
    supplier = Supplier.objects.filter(pk=supplier_id).first() if supplier_id else None

    report_data = get_expenses_report_data(from_date, to_date, project, supplier)

    context = {
        'report_data': report_data,
        'from_date': from_date,
        'to_date': to_date,
        'selected_project': project,
        'selected_supplier': supplier,
    }

    if output_format == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="expenses_report.csv"'
        response.write('\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        writer.writerow(['التاريخ', 'البيان', 'الخزنة', 'المشروع', 'المورد', 'المبلغ'])
        for expense in report_data['expenses']:
            writer.writerow([
                expense.date,
                expense.description,
                expense.safe.name,
                expense.project.name if expense.project else '',
                expense.supplier.name if expense.supplier else '',
                expense.amount
            ])
        writer.writerow(['الإجمالي', '', '', '', '', report_data['total_expenses']])
        return response

    return render(request, 'accounting/reports/expenses_report_view.html', context)
