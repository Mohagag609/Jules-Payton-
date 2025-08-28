from django import forms
from django.forms.widgets import TextInput, Select, NumberInput, DateInput, Textarea
from datetime import date
from .models import (
    Partner, Safe, Customer, Supplier, Unit, Project, Item, StockMove,
    Contract, ReceiptVoucher, PaymentVoucher
)

class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['code', 'name', 'share_percent', 'opening_balance', 'notes']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'share_percent': forms.NumberInput(attrs={'class': 'form-input'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

class SafeForm(forms.ModelForm):
    class Meta:
        model = Safe
        fields = ['name', 'is_partner_wallet', 'partner']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'is_partner_wallet': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'partner': forms.Select(attrs={'class': 'form-select'}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['code', 'name', 'phone', 'email', 'address', 'is_active']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone']

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['code', 'name', 'building_no', 'type', 'price_total', 'category', 'partners_group']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['code', 'name', 'type', 'start_date', 'end_date', 'status', 'budget']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['code', 'name', 'uom', 'unit_price', 'supplier']

class StockMoveForm(forms.ModelForm):
    class Meta:
        model = StockMove
        fields = ['item', 'project', 'qty', 'direction', 'date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'code', 'customer', 'unit', 'unit_value', 'down_payment',
            'installments_count', 'schedule_type', 'start_date', 'partners_group'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter units to only show available ones
        self.fields['unit'].queryset = Unit.objects.filter(contract__isnull=True)
        # Style the form inputs
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                 field.widget.attrs.update({
                    'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
                })

class InstallmentPaymentForm(forms.Form):
    amount = forms.DecimalField(label="المبلغ المدفوع", max_digits=15, decimal_places=2)
    safe = forms.ModelChoiceField(queryset=Safe.objects.all(), label="الخزنة")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="تاريخ السداد")

class ReceiptVoucherForm(forms.ModelForm):
    class Meta:
        model = ReceiptVoucher
        fields = ['date', 'amount', 'safe', 'description', 'customer', 'partner', 'contract']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the form inputs
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            })

class PaymentVoucherForm(forms.ModelForm):
    class Meta:
        model = PaymentVoucher
        fields = ['date', 'amount', 'safe', 'description', 'supplier', 'project', 'expense_head']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the form inputs
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            })
