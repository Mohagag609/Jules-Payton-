"""
Base views and mixins for the accounting app
"""
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
import logging

logger = logging.getLogger('accounting')


class HTMXResponseMixin:
    """Mixin for handling HTMX responses with error handling"""
    
    def handle_form_submission(self, request, form, success_template, form_template, 
                             object_name='object', success_message=None, 
                             htmx_trigger=None, target_id=None):
        """
        Handle form submission with proper error handling and HTMX support
        
        Args:
            request: The HTTP request
            form: The form instance
            success_template: Template to render on success
            form_template: Template to render on failure
            object_name: Name of the object for the success message
            success_message: Custom success message (optional)
            htmx_trigger: HTMX trigger name (optional)
            target_id: Target element ID for HTMX swap
        """
        if form.is_valid():
            try:
                obj = form.save()
                
                # Create success message
                if not success_message:
                    success_message = f'تم إضافة {object_name} بنجاح!'
                messages.success(request, success_message)
                
                # Prepare response
                response = render(request, success_template, {object_name: obj})
                
                # Add HTMX trigger if specified
                if htmx_trigger:
                    response['HX-Trigger'] = htmx_trigger
                
                logger.info(f'Successfully created {object_name}: {obj}')
                return response
                
            except Exception as e:
                logger.error(f'Error creating {object_name}: {str(e)}', exc_info=True)
                messages.error(request, f'حدث خطأ: {str(e)}')
                return render(request, form_template, {'form': form}, status=400)
        else:
            # Return form with errors
            logger.warning(f'Form validation failed for {object_name}: {form.errors}')
            return render(request, form_template, {'form': form}, status=400)
    
    def handle_update(self, request, form, instance, success_template, form_template,
                     object_name='object', success_message=None):
        """Handle object update with error handling"""
        if form.is_valid():
            try:
                obj = form.save()
                
                if not success_message:
                    success_message = f'تم تحديث {object_name} بنجاح!'
                messages.success(request, success_message)
                
                response = render(request, success_template, {object_name: obj})
                logger.info(f'Successfully updated {object_name}: {obj}')
                return response
                
            except Exception as e:
                logger.error(f'Error updating {object_name}: {str(e)}', exc_info=True)
                messages.error(request, f'حدث خطأ في التحديث: {str(e)}')
                return render(request, form_template, 
                            {'form': form, object_name: instance}, status=400)
        else:
            logger.warning(f'Update form validation failed for {object_name}: {form.errors}')
            return render(request, form_template, 
                        {'form': form, object_name: instance}, status=400)
    
    def handle_delete(self, request, instance, object_name='object', success_message=None):
        """Handle object deletion with error handling"""
        try:
            instance_str = str(instance)
            instance.delete()
            
            if not success_message:
                success_message = f'تم حذف {object_name} بنجاح!'
            messages.success(request, success_message)
            
            logger.info(f'Successfully deleted {object_name}: {instance_str}')
            return HttpResponse("")  # Empty response for HTMX delete
            
        except Exception as e:
            logger.error(f'Error deleting {object_name}: {str(e)}', exc_info=True)
            error_msg = 'لا يمكن حذف هذا العنصر لوجود بيانات مرتبطة به' if 'PROTECT' in str(e) else str(e)
            messages.error(request, error_msg)
            return HttpResponse(f'<div class="text-red-600">{error_msg}</div>', status=400)


def create_default_data():
    """Create default data for the system if not exists"""
    from accounting.models import Safe, Unit
    
    # Create default safe
    if not Safe.objects.exists():
        Safe.objects.create(
            code='MAIN',
            name='الخزنة الرئيسية',
            balance=0
        )
        logger.info('Created default safe')
    
    # Create default units
    default_units = [
        {'code': 'PCS', 'name': 'قطعة'},
        {'code': 'M', 'name': 'متر'},
        {'code': 'KG', 'name': 'كيلو'},
        {'code': 'BOX', 'name': 'كرتونة'},
    ]
    
    for unit_data in default_units:
        Unit.objects.get_or_create(
            code=unit_data['code'],
            defaults={'name': unit_data['name']}
        )
    logger.info('Default data created/verified')