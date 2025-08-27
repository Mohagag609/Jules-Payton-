import csv
from datetime import date, timedelta
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from weasyprint import HTML, CSS

from accounting.models import Safe
from accounting.services.reports import get_treasury_report_data

@login_required
def report_index_view(request):
    """
    Shows the main page for selecting a report.
    """
    safes = Safe.objects.all()
    today = date.today()
    first_day_of_month = today.replace(day=1)

    context = {
        'page_title': 'التقارير',
        'safes': safes,
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
