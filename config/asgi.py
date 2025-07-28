"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import sys

from django.core.asgi import get_asgi_application

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


application = get_asgi_application()
