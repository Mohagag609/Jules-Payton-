from django import forms
from datetime import date
from .models import (
    Partner, Safe, Customer, Supplier, Unit, Project, Item, StockMove,
    Contract, ReceiptVoucher, PaymentVoucher
)

class BaseStyledForm(forms.ModelForm):
    """A base form to apply consistent styling to all model forms."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            common_classes = 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'

            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500'})
            elif isinstance(widget, forms.Textarea):
                widget.attrs.update({'class': f'{common_classes} h-24'})
            else:
                widget.attrs.update({'class': common_classes})

class PartnerForm(BaseStyledForm):
    class Meta:
        model = Partner
        fields = ['code', 'name', 'share_percent', 'opening_balance', 'notes']

class SafeForm(BaseStyledForm):
    class Meta:
        model = Safe
        fields = ['name', 'is_partner_wallet', 'partner']

class CustomerForm(BaseStyledForm):
    class Meta:
        model = Customer
        fields = ['code', 'name', 'phone', 'email', 'address', 'is_active']

class SupplierForm(BaseStyledForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone']

class UnitForm(BaseStyledForm):
    class Meta:
        model = Unit
        fields = ['code', 'name', 'building_no', 'type', 'price_total', 'category', 'partners_group']

class ProjectForm(BaseStyledForm):
    class Meta:
        model = Project
        fields = ['code', 'name', 'type', 'start_date', 'end_date', 'status', 'budget']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ItemForm(BaseStyledForm):
    class Meta:
        model = Item
        fields = ['code', 'name', 'uom', 'unit_price', 'supplier', 'min_stock_level']

class StockMoveForm(BaseStyledForm):
    class Meta:
        model = StockMove
        fields = ['item', 'project', 'qty', 'direction', 'date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class ContractForm(BaseStyledForm):
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
        # Custom queryset for the 'unit' field
        if 'instance' not in kwargs:
             self.fields['unit'].queryset = Unit.objects.filter(contract__isnull=True)

class InstallmentPaymentForm(forms.Form):
    amount = forms.DecimalField(label="المبلغ المدفوع", max_digits=15, decimal_places=2)
    safe = forms.ModelChoiceField(queryset=Safe.objects.all(), label="الخزنة")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="تاريخ السداد")

    def __init__(self, *args, **kwargs):
        installment = kwargs.pop('installment', None)
        super().__init__(*args, **kwargs)
        if installment:
            self.fields['amount'].initial = installment.remaining_to_pay
            self.fields['date'].initial = date.today()

        # Apply styling
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
            })

class ReceiptVoucherForm(BaseStyledForm):
    class Meta:
        model = ReceiptVoucher
        fields = ['date', 'amount', 'safe', 'description', 'customer', 'partner', 'contract']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

class PaymentVoucherForm(BaseStyledForm):
    class Meta:
        model = PaymentVoucher
        fields = ['date', 'amount', 'safe', 'description', 'supplier', 'project', 'expense_head']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}
