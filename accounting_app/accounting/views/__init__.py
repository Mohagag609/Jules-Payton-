# Import all views for easier access
from .base import HTMXResponseMixin, create_default_data
from .customers import *
from .suppliers import *
from .partners import *
from .safes import *
from .units import *
from .projects_store import *
from .contracts import *
from .installments import *
from .vouchers import *
from .settlements import *
from .reports import *

# Run default data creation on import
try:
    create_default_data()
except Exception as e:
    import logging
    logger = logging.getLogger('accounting')
    logger.warning(f'Could not create default data: {e}')