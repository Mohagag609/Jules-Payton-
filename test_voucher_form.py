#!/usr/bin/env python
import os
import sys
import django

# Add the project to the Python path
sys.path.insert(0, '/workspace/accounting_app')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounting.forms import PaymentVoucherForm, ReceiptVoucherForm
from accounting.models import Safe

# Test the forms
print("=== Testing PaymentVoucherForm ===")
form = PaymentVoucherForm()
print("Required fields:")
for field_name, field in form.fields.items():
    print(f"  {field_name}: required={field.required}")

print("\n=== Testing with sample data ===")
# Get a safe if exists
try:
    safe = Safe.objects.first()
    if safe:
        test_data = {
            'date': '2024-01-01',
            'amount': '100.00',
            'safe': safe.id,
            'description': 'Test payment',
        }
        form = PaymentVoucherForm(data=test_data)
        print(f"Form valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Errors: {form.errors}")
    else:
        print("No Safe objects found in database")
except Exception as e:
    print(f"Error: {e}")