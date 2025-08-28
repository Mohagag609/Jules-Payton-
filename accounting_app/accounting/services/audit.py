"""
Audit Logging Service
Provides comprehensive tracking of all system changes.
"""

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from accounting.models import AuditLog
from core.feature_flags import LEGACY_AUDIT_LOG_ENABLED


class AuditService:
    """
    Service for logging all system actions and changes.
    """
    
    @staticmethod
    def log_action(user, action, description, obj=None, details=None, request=None):
        """
        Log an action to the audit trail.
        
        Args:
            user: The user performing the action
            action: The type of action (create, update, delete, other)
            description: Human-readable description of the action
            obj: The object being acted upon (optional)
            details: Additional details as dict (optional)
            request: The HTTP request object (optional)
        """
        if not LEGACY_AUDIT_LOG_ENABLED:
            return None
            
        audit_log = AuditLog(
            user=user,
            action=action,
            description=description,
            details=details or {},
            timestamp=timezone.now()
        )
        
        # Add object reference if provided
        if obj:
            audit_log.content_type = ContentType.objects.get_for_model(obj)
            audit_log.object_id = obj.pk
        
        # Extract request metadata if available
        if request:
            audit_log.ip_address = AuditService._get_client_ip(request)
            audit_log.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        audit_log.save()
        return audit_log
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def log_create(user, obj, request=None):
        """Log object creation."""
        model_name = obj._meta.verbose_name
        return AuditService.log_action(
            user=user,
            action=AuditLog.Action.CREATE,
            description=f"إنشاء {model_name} جديد",
            obj=obj,
            details={'id': obj.pk, 'str': str(obj)},
            request=request
        )
    
    @staticmethod
    def log_update(user, obj, changes, request=None):
        """Log object update with field changes."""
        model_name = obj._meta.verbose_name
        return AuditService.log_action(
            user=user,
            action=AuditLog.Action.UPDATE,
            description=f"تعديل {model_name}",
            obj=obj,
            details={'changes': changes},
            request=request
        )
    
    @staticmethod
    def log_delete(user, obj, request=None):
        """Log object deletion."""
        model_name = obj._meta.verbose_name
        return AuditService.log_action(
            user=user,
            action=AuditLog.Action.DELETE,
            description=f"حذف {model_name}",
            details={'deleted_object': str(obj), 'id': obj.pk},
            request=request
        )
    
    @staticmethod
    def log_bulk_action(user, action_type, objects, description, request=None):
        """Log bulk actions on multiple objects."""
        object_ids = [obj.pk for obj in objects]
        model_name = objects[0]._meta.verbose_name_plural if objects else 'objects'
        
        return AuditService.log_action(
            user=user,
            action=AuditLog.Action.OTHER,
            description=f"{description} ({len(objects)} {model_name})",
            details={
                'action_type': action_type,
                'object_ids': object_ids,
                'count': len(objects)
            },
            request=request
        )
    
    @staticmethod
    def get_object_history(obj, limit=50):
        """Get audit history for a specific object."""
        content_type = ContentType.objects.get_for_model(obj)
        return AuditLog.objects.filter(
            content_type=content_type,
            object_id=obj.pk
        ).order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_user_activity(user, limit=100):
        """Get recent activity for a specific user."""
        return AuditLog.objects.filter(
            user=user
        ).order_by('-timestamp')[:limit]