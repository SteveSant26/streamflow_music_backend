# Configuración de tests para pytest (si se necesita)

import os
import sys
import django
from django.conf import settings

# Configurar Django para tests
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
    django.setup()

def pytest_configure(config):
    """Configuración inicial de pytest"""
    # Configurar logging para tests
    import logging
    logging.disable(logging.CRITICAL)

def pytest_collection_modifyitems(config, items):
    """Modificar items de colección de tests"""
    # Aquí se pueden agregar configuraciones específicas
    pass
