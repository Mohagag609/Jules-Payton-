"""
Feature Flags for legacy system features.
These can be toggled to enable/disable specific features during migration.
"""

from django.conf import settings

# Get feature flags from settings or use defaults
FEATURE_FLAGS = getattr(settings, 'FEATURE_FLAGS', {})

# Legacy Features
LEGACY_PARTNER_RETURN_ENABLED = FEATURE_FLAGS.get('LEGACY_PARTNER_RETURN_ENABLED', True)
LEGACY_SMART_INSTALLMENTS_ENABLED = FEATURE_FLAGS.get('LEGACY_SMART_INSTALLMENTS_ENABLED', True)
LEGACY_COMMISSION_TRACKING_ENABLED = FEATURE_FLAGS.get('LEGACY_COMMISSION_TRACKING_ENABLED', True)
LEGACY_INLINE_EDITING_ENABLED = FEATURE_FLAGS.get('LEGACY_INLINE_EDITING_ENABLED', True)
LEGACY_UNDO_REDO_ENABLED = FEATURE_FLAGS.get('LEGACY_UNDO_REDO_ENABLED', True)
LEGACY_KEYBOARD_SHORTCUTS_ENABLED = FEATURE_FLAGS.get('LEGACY_KEYBOARD_SHORTCUTS_ENABLED', True)
LEGACY_IMPORT_EXPORT_ENABLED = FEATURE_FLAGS.get('LEGACY_IMPORT_EXPORT_ENABLED', True)
LEGACY_AUDIT_LOG_ENABLED = FEATURE_FLAGS.get('LEGACY_AUDIT_LOG_ENABLED', True)

# UI/UX Features
LUXURY_THEME_ENABLED = FEATURE_FLAGS.get('LUXURY_THEME_ENABLED', True)
TOAST_NOTIFICATIONS_ENABLED = FEATURE_FLAGS.get('TOAST_NOTIFICATIONS_ENABLED', True)
GROUPED_VIEWS_ENABLED = FEATURE_FLAGS.get('GROUPED_VIEWS_ENABLED', True)
EMPTY_STATES_ENABLED = FEATURE_FLAGS.get('EMPTY_STATES_ENABLED', True)

# Development Features
DEBUG_MODE = FEATURE_FLAGS.get('DEBUG_MODE', settings.DEBUG)


def is_feature_enabled(feature_name):
    """
    Check if a specific feature is enabled.
    """
    return globals().get(feature_name, False)


def get_enabled_features():
    """
    Get a list of all enabled features.
    """
    return [
        name for name, value in globals().items()
        if name.endswith('_ENABLED') and value is True
    ]