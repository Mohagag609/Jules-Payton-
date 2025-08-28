"""
Additional forms for new models
"""

from django import forms
from decimal import Decimal
from django.db import models
from .models import UnitPartner, Broker, Transfer, UserSettings


class UnitPartnerForm(forms.ModelForm):
    """Form for adding partners to units"""
    class Meta:
        model = UnitPartner
        fields = ['partner', 'percent']
        widgets = {
            'partner': forms.Select(attrs={'class': 'form-select form-select-luxury'}),
            'percent': forms.NumberInput(attrs={
                'class': 'form-control form-control-luxury',
                'step': '0.01',
                'min': '0.01',
                'max': '100.00'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.unit = kwargs.pop('unit', None)
        super().__init__(*args, **kwargs)
        
        if self.unit:
            # Exclude partners already assigned to this unit
            existing_partner_ids = UnitPartner.objects.filter(
                unit=self.unit
            ).values_list('partner_id', flat=True)
            
            from .models import Partner
            self.fields['partner'].queryset = Partner.objects.filter(
                is_active=True
            ).exclude(id__in=existing_partner_ids)
    
    def clean_percent(self):
        percent = self.cleaned_data.get('percent')
        
        if self.unit:
            # Check if total percentage doesn't exceed 100%
            current_total = UnitPartner.objects.filter(
                unit=self.unit
            ).exclude(
                pk=self.instance.pk if self.instance.pk else None
            ).aggregate(
                total=models.Sum('percent')
            )['total'] or Decimal('0')
            
            if current_total + percent > 100:
                raise forms.ValidationError(
                    f"إجمالي النسب سيتجاوز 100%. النسبة الحالية: {current_total}%"
                )
        
        return percent


class BrokerForm(forms.ModelForm):
    """Form for brokers"""
    class Meta:
        model = Broker
        fields = ['name', 'phone', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-luxury'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-luxury'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-luxury', 'rows': 3}),
        }


class TransferForm(forms.ModelForm):
    """Form for transfers between safes"""
    class Meta:
        model = Transfer
        fields = ['from_safe', 'to_safe', 'amount', 'date', 'notes']
        widgets = {
            'from_safe': forms.Select(attrs={'class': 'form-select form-select-luxury'}),
            'to_safe': forms.Select(attrs={'class': 'form-select form-select-luxury'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control form-control-luxury'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-luxury'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-luxury', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        from_safe = cleaned_data.get('from_safe')
        to_safe = cleaned_data.get('to_safe')
        amount = cleaned_data.get('amount')
        
        if from_safe and to_safe and from_safe == to_safe:
            raise forms.ValidationError("لا يمكن التحويل من وإلى نفس الخزنة")
        
        if from_safe and amount and from_safe.balance < amount:
            raise forms.ValidationError(
                f"رصيد الخزنة '{from_safe.name}' غير كافٍ. الرصيد الحالي: {from_safe.balance}"
            )
        
        return cleaned_data


class UserSettingsForm(forms.ModelForm):
    """Form for user settings"""
    class Meta:
        model = UserSettings
        fields = ['theme', 'font_size', 'enable_shortcuts', 'enable_inline_editing', 'enable_undo_redo']
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-select form-select-luxury'}),
            'font_size': forms.NumberInput(attrs={
                'class': 'form-control form-control-luxury',
                'min': '12',
                'max': '24'
            }),
            'enable_shortcuts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enable_inline_editing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enable_undo_redo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }