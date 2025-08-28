#!/usr/bin/env python3
"""
Script to update all views to use the new base mixin and error handling
"""

import os
import sys

# Add the project to the Python path
sys.path.insert(0, '/workspace/accounting_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Views update configuration
VIEWS_CONFIG = {
    'partners': {
        'model': 'Partner',
        'form': 'PartnerForm',
        'object_name': 'partner',
        'arabic_name': 'الشريك',
        'trigger': 'partnerAdded',
        'color': 'orange'
    },
    'safes': {
        'model': 'Safe',
        'form': 'SafeForm',
        'object_name': 'safe',
        'arabic_name': 'الخزنة',
        'trigger': 'safeAdded',
        'color': 'indigo'
    },
    'units': {
        'model': 'Unit',
        'form': 'UnitForm',
        'object_name': 'unit',
        'arabic_name': 'الوحدة',
        'trigger': 'unitAdded',
        'color': 'teal'
    }
}

# Template for views
VIEW_TEMPLATE = """from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
import json
import logging

from accounting.models import {model}
from accounting.forms import {form}
from .base import HTMXResponseMixin

logger = logging.getLogger('accounting')


class {model}ViewMixin(HTMXResponseMixin):
    \"\"\"Mixin for {object_name} views\"\"\"
    pass


@login_required
def {object_name}_list_view(request):
    \"\"\"List all {object_name}s and handle creation\"\"\"
    mixin = {model}ViewMixin()
    form = {form}(request.POST or None)
    
    if request.method == 'POST':
        response = mixin.handle_form_submission(
            request=request,
            form=form,
            success_template='accounting/{object_name}s/_row.html',
            form_template='accounting/{object_name}s/_form_container.html',
            object_name='{object_name}',
            success_message='تم إضافة {arabic_name} بنجاح!',
            htmx_trigger='{trigger}'
        )
        return response

    {object_name}s = {model}.objects.all()
    context = {{
        '{object_name}s': {object_name}s,
        'form': form,
        'page_title': '{arabic_name}ات'
    }}
    return render(request, 'accounting/{object_name}s/list.html', context)


@login_required
@require_POST
def {object_name}_update_view(request, pk):
    \"\"\"Update {object_name}\"\"\"
    mixin = {model}ViewMixin()
    {object_name} = get_object_or_404({model}, pk=pk)
    form = {form}(request.POST, instance={object_name})
    
    return mixin.handle_update(
        request=request,
        form=form,
        instance={object_name},
        success_template='accounting/{object_name}s/_row.html',
        form_template='accounting/{object_name}s/_form_container.html',
        object_name='{object_name}',
        success_message=f'تم تحديث بيانات {arabic_name} "{{{object_name}.name}}" بنجاح!'
    )


@login_required
def {object_name}_get_form_view(request, pk):
    \"\"\"Get {object_name} form for editing\"\"\"
    {object_name} = get_object_or_404({model}, pk=pk)
    form = {form}(instance={object_name})
    return render(request, 'accounting/{object_name}s/_form_container.html', {{'form': form, '{object_name}': {object_name}}})


@login_required
@require_http_methods(["DELETE"])
def {object_name}_delete_view(request, pk):
    \"\"\"Delete {object_name}\"\"\"
    mixin = {model}ViewMixin()
    {object_name} = get_object_or_404({model}, pk=pk)
    
    response = mixin.handle_delete(
        request=request,
        instance={object_name},
        object_name='{arabic_name}',
        success_message=f'تم حذف {arabic_name} "{{{object_name}.name}}" بنجاح!'
    )
    
    # Add HTMX trigger for toast notification
    if response.status_code == 200:
        toast_event = {{
            "showToast": {{
                "message": f'تم حذف {arabic_name} "{{{object_name}.name}}" بنجاح!',
                "type": "success"
            }}
        }}
        response['HX-Trigger'] = json.dumps(toast_event)
    else:
        toast_event = {{
            "showToast": {{
                "message": "لا يمكن حذف هذا {arabic_name} لوجود بيانات مرتبطة به.",
                "type": "error"
            }}
        }}
        response['HX-Trigger'] = json.dumps(toast_event)
    
    return response
"""

print("Configuration ready. Update views manually using the template above.")
print("\nFor each view file, update with:")
for view_name, config in VIEWS_CONFIG.items():
    print(f"\n{view_name}.py:")
    print(f"  - Model: {config['model']}")
    print(f"  - Form: {config['form']}")
    print(f"  - Trigger: {config['trigger']}")
    print(f"  - Color: {config['color']}")