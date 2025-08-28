"""
Undo/Redo Middleware
Implements undo/redo functionality for user actions.
"""

import json
from django.utils.deprecation import MiddlewareMixin
from core.feature_flags import LEGACY_UNDO_REDO_ENABLED


class UndoRedoMiddleware(MiddlewareMixin):
    """
    Middleware to track state changes for undo/redo functionality.
    """
    
    STACK_SIZE = 50  # Maximum number of states to keep
    
    def process_request(self, request):
        """Initialize undo/redo stack in session if needed."""
        if not LEGACY_UNDO_REDO_ENABLED:
            return
            
        if 'undo_stack' not in request.session:
            request.session['undo_stack'] = []
            request.session['undo_index'] = -1
    
    def process_response(self, request, response):
        """Save state after successful POST/PUT/DELETE requests."""
        if not LEGACY_UNDO_REDO_ENABLED:
            return response
            
        # Only track state-changing methods
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Check if the response was successful
            if 200 <= response.status_code < 300:
                self._save_state(request)
        
        return response
    
    def _save_state(self, request):
        """Save current state to the undo stack."""
        # This is a simplified implementation
        # In production, you'd want to serialize the actual state changes
        
        state_snapshot = {
            'timestamp': str(timezone.now()),
            'method': request.method,
            'path': request.path,
            'user': request.user.username if request.user.is_authenticated else 'anonymous',
        }
        
        stack = request.session.get('undo_stack', [])
        index = request.session.get('undo_index', -1)
        
        # Remove any states after current index (for redo functionality)
        stack = stack[:index + 1]
        
        # Add new state
        stack.append(state_snapshot)
        
        # Limit stack size
        if len(stack) > self.STACK_SIZE:
            stack.pop(0)
        
        request.session['undo_stack'] = stack
        request.session['undo_index'] = len(stack) - 1
        request.session.modified = True


class LockMiddleware(MiddlewareMixin):
    """
    Middleware to implement application locking functionality.
    """
    
    EXEMPT_PATHS = ['/login/', '/unlock/', '/api/']
    
    def process_request(self, request):
        """Check if app is locked and redirect if needed."""
        # Skip for exempt paths
        for path in self.EXEMPT_PATHS:
            if request.path.startswith(path):
                return
        
        # Check if user has lock settings
        if request.user.is_authenticated and hasattr(request.user, 'settings'):
            settings = request.user.settings
            if settings.is_locked and not request.session.get('unlocked'):
                # Redirect to unlock page
                from django.shortcuts import redirect
                return redirect('unlock_app')


class ThemeMiddleware(MiddlewareMixin):
    """
    Middleware to apply user theme preferences.
    """
    
    def process_request(self, request):
        """Set theme in request for use in templates."""
        theme = 'dark'  # Default
        font_size = 16  # Default
        
        if request.user.is_authenticated and hasattr(request.user, 'settings'):
            settings = request.user.settings
            theme = settings.theme
            font_size = settings.font_size
        
        request.theme = theme
        request.font_size = font_size