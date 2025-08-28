"""
Advanced Import/Export Service
Handles CSV, Excel import/export with validation and error handling.
"""

import csv
import io
import json
from datetime import datetime
from decimal import Decimal
import pandas as pd
from django.db import transaction
from django.core.exceptions import ValidationError

from accounting.models import (
    Customer, Unit, Partner, Contract, Broker,
    Safe, UnitPartner, PartnersGroup
)
from accounting.services.audit import AuditService
from core.feature_flags import LEGACY_IMPORT_EXPORT_ENABLED


class ImportExportService:
    """
    Service for importing and exporting data in various formats.
    """
    
    SUPPORTED_MODELS = {
        'customers': {
            'model': Customer,
            'fields': ['code', 'name', 'phone', 'email', 'national_id', 'address', 'status', 'notes'],
            'required': ['name', 'phone'],
            'unique': ['code'],
            'arabic_headers': {
                'code': 'الكود',
                'name': 'الاسم',
                'phone': 'الهاتف',
                'email': 'البريد الإلكتروني',
                'national_id': 'الرقم القومي',
                'address': 'العنوان',
                'status': 'الحالة',
                'notes': 'ملاحظات'
            }
        },
        'units': {
            'model': Unit,
            'fields': ['code', 'name', 'building_no', 'floor', 'type', 'price_total', 'area', 'status', 'notes'],
            'required': ['code', 'name', 'price_total'],
            'unique': ['code'],
            'arabic_headers': {
                'code': 'كود الوحدة',
                'name': 'اسم الوحدة',
                'building_no': 'رقم المبنى',
                'floor': 'الدور',
                'type': 'النوع',
                'price_total': 'السعر',
                'area': 'المساحة',
                'status': 'الحالة',
                'notes': 'ملاحظات'
            }
        },
        'partners': {
            'model': Partner,
            'fields': ['name', 'phone', 'email', 'is_active'],
            'required': ['name'],
            'unique': ['name'],
            'arabic_headers': {
                'name': 'الاسم',
                'phone': 'الهاتف',
                'email': 'البريد الإلكتروني',
                'is_active': 'نشط'
            }
        },
        'brokers': {
            'model': Broker,
            'fields': ['name', 'phone', 'notes'],
            'required': ['name'],
            'unique': ['name'],
            'arabic_headers': {
                'name': 'اسم السمسار',
                'phone': 'الهاتف',
                'notes': 'ملاحظات'
            }
        }
    }
    
    @classmethod
    def export_csv(cls, model_name, queryset=None, user=None):
        """
        Export data to CSV format.
        """
        if not LEGACY_IMPORT_EXPORT_ENABLED:
            raise PermissionError("خاصية التصدير غير مفعلة")
            
        if model_name not in cls.SUPPORTED_MODELS:
            raise ValueError(f"Model {model_name} is not supported for export")
            
        config = cls.SUPPORTED_MODELS[model_name]
        model = config['model']
        
        if queryset is None:
            queryset = model.objects.all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers in Arabic
        headers = [config['arabic_headers'].get(field, field) for field in config['fields']]
        writer.writerow(headers)
        
        # Write data
        for obj in queryset:
            row = []
            for field in config['fields']:
                value = getattr(obj, field, '')
                if isinstance(value, Decimal):
                    value = float(value)
                elif isinstance(value, bool):
                    value = 'نعم' if value else 'لا'
                elif value is None:
                    value = ''
                row.append(str(value))
            writer.writerow(row)
        
        # Log export
        AuditService.log_action(
            user=user,
            action='export',
            description=f"تصدير {queryset.count()} {model._meta.verbose_name_plural} إلى CSV",
            details={'model': model_name, 'count': queryset.count()}
        )
        
        output.seek(0)
        return output.getvalue()
    
    @classmethod
    def export_excel(cls, data_dict, filename='export.xlsx', user=None):
        """
        Export multiple models to Excel with multiple sheets.
        """
        if not LEGACY_IMPORT_EXPORT_ENABLED:
            raise PermissionError("خاصية التصدير غير مفعلة")
            
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, model_data in data_dict.items():
                if 'model_name' not in model_data:
                    continue
                    
                model_name = model_data['model_name']
                queryset = model_data.get('queryset')
                
                if model_name not in cls.SUPPORTED_MODELS:
                    continue
                
                config = cls.SUPPORTED_MODELS[model_name]
                model = config['model']
                
                if queryset is None:
                    queryset = model.objects.all()
                
                # Prepare data
                data = []
                for obj in queryset:
                    row = {}
                    for field in config['fields']:
                        value = getattr(obj, field, '')
                        if isinstance(value, Decimal):
                            value = float(value)
                        row[config['arabic_headers'].get(field, field)] = value
                    data.append(row)
                
                # Create DataFrame and write to Excel
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)  # Excel sheet name limit
                
                # Format the worksheet
                worksheet = writer.sheets[sheet_name[:31]]
                for idx, col in enumerate(df.columns):
                    worksheet.column_dimensions[chr(65 + idx)].width = 15
        
        output.seek(0)
        
        # Log export
        AuditService.log_action(
            user=user,
            action='export',
            description=f"تصدير بيانات متعددة إلى Excel",
            details={'sheets': list(data_dict.keys())}
        )
        
        return output.getvalue()
    
    @classmethod
    @transaction.atomic
    def import_csv(cls, model_name, file_content, user=None):
        """
        Import data from CSV with validation.
        """
        if not LEGACY_IMPORT_EXPORT_ENABLED:
            raise PermissionError("خاصية الاستيراد غير مفعلة")
            
        if model_name not in cls.SUPPORTED_MODELS:
            raise ValueError(f"Model {model_name} is not supported for import")
            
        config = cls.SUPPORTED_MODELS[model_name]
        model = config['model']
        
        # Parse CSV
        csv_file = io.StringIO(file_content.decode('utf-8-sig'))  # Handle BOM
        reader = csv.DictReader(csv_file)
        
        # Reverse map Arabic headers to field names
        header_map = {v: k for k, v in config['arabic_headers'].items()}
        
        imported_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):  # Start from 2 (header is 1)
            try:
                # Map Arabic headers to field names
                data = {}
                for arabic_header, value in row.items():
                    field_name = header_map.get(arabic_header, arabic_header)
                    if field_name in config['fields']:
                        data[field_name] = value.strip() if value else ''
                
                # Validate required fields
                for field in config['required']:
                    if not data.get(field):
                        raise ValidationError(f"الحقل المطلوب '{field}' مفقود")
                
                # Handle special fields
                if 'is_active' in data:
                    data['is_active'] = data['is_active'].lower() in ['نعم', 'yes', 'true', '1']
                
                if 'price_total' in data and data['price_total']:
                    data['price_total'] = Decimal(data['price_total'].replace(',', ''))
                
                if 'area' in data and data['area']:
                    data['area'] = Decimal(data['area'].replace(',', ''))
                
                # Check for unique constraints
                for unique_field in config.get('unique', []):
                    if data.get(unique_field):
                        exists = model.objects.filter(**{unique_field: data[unique_field]}).exists()
                        if exists:
                            # Update existing instead of creating new
                            obj = model.objects.get(**{unique_field: data[unique_field]})
                            for field, value in data.items():
                                if value != '':  # Only update non-empty values
                                    setattr(obj, field, value)
                            obj.save()
                            imported_count += 1
                            continue
                
                # Create new object
                obj = model(**data)
                obj.full_clean()  # Validate
                obj.save()
                imported_count += 1
                
            except Exception as e:
                errors.append({
                    'row': row_num,
                    'data': row,
                    'error': str(e)
                })
        
        # Log import
        AuditService.log_action(
            user=user,
            action='import',
            description=f"استيراد {imported_count} {model._meta.verbose_name_plural} من CSV",
            details={
                'model': model_name,
                'imported': imported_count,
                'errors': len(errors)
            }
        )
        
        return {
            'success': True,
            'imported': imported_count,
            'errors': errors
        }
    
    @classmethod
    def generate_template(cls, model_name):
        """
        Generate a CSV template for a model.
        """
        if model_name not in cls.SUPPORTED_MODELS:
            raise ValueError(f"Model {model_name} is not supported")
            
        config = cls.SUPPORTED_MODELS[model_name]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers in Arabic
        headers = [config['arabic_headers'].get(field, field) for field in config['fields']]
        writer.writerow(headers)
        
        # Add sample row
        sample_data = {
            'code': 'U001',
            'name': 'مثال',
            'phone': '01234567890',
            'email': 'example@example.com',
            'national_id': '12345678901234',
            'address': 'العنوان هنا',
            'status': 'نشط',
            'notes': 'ملاحظات اختيارية',
            'building_no': 'A',
            'floor': '3',
            'type': 'سكني',
            'price_total': '1000000',
            'area': '150',
            'is_active': 'نعم'
        }
        
        sample_row = []
        for field in config['fields']:
            sample_value = sample_data.get(field, '')
            sample_row.append(sample_value)
        writer.writerow(sample_row)
        
        output.seek(0)
        return output.getvalue()
    
    @classmethod
    def backup_all_data(cls, user=None):
        """
        Create a complete backup of all data in JSON format.
        """
        backup_data = {
            'version': '2.0',
            'created_at': datetime.now().isoformat(),
            'created_by': user.username if user else 'system',
            'data': {}
        }
        
        # Export all models
        models_to_backup = [
            'customers', 'units', 'partners', 'brokers',
            'contracts', 'installments', 'safes', 'vouchers'
        ]
        
        for model_name in models_to_backup:
            if model_name in cls.SUPPORTED_MODELS:
                config = cls.SUPPORTED_MODELS[model_name]
                model = config['model']
                
                # Serialize all objects
                objects = []
                for obj in model.objects.all():
                    obj_data = {}
                    for field in obj._meta.fields:
                        value = getattr(obj, field.name)
                        if isinstance(value, Decimal):
                            value = str(value)
                        elif hasattr(value, 'isoformat'):
                            value = value.isoformat()
                        obj_data[field.name] = value
                    objects.append(obj_data)
                
                backup_data['data'][model_name] = objects
        
        # Log backup
        AuditService.log_action(
            user=user,
            action='backup',
            description="إنشاء نسخة احتياطية كاملة للنظام",
            details={'models': list(backup_data['data'].keys())}
        )
        
        return json.dumps(backup_data, ensure_ascii=False, indent=2)