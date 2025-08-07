"""
Configuración base para tests de user_profile
"""

import os
import sys
from pathlib import Path

# Configurar paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

# Configurar Django para tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django
from django.conf import settings

django.setup()


class UserProfileTestConfig:
    """Configuración específica para tests de user_profile"""

    # Base de datos de testing en memoria
    TEST_DATABASE = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

    # Apps necesarias para los tests
    REQUIRED_APPS = [
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "apps.user_profile",
    ]

    @classmethod
    def setup_test_environment(cls):
        """Configura el entorno de testing"""
        # Configurar base de datos de testing
        if "test" in sys.argv:
            settings.DATABASES["default"] = cls.TEST_DATABASE

        return True


# Funciones helper para tests
def create_test_user_profile(email="test@example.com", **kwargs):
    """Helper para crear un perfil de usuario de prueba"""
    from uuid import uuid4

    from apps.user_profile.infrastructure.models.user_profile import UserProfile

    defaults = {"id": str(uuid4()), "email": email, "profile_picture": None}
    defaults.update(kwargs)

    return UserProfile.objects.create(**defaults)


def create_test_user_entity(email="test@example.com", **kwargs):
    """Helper para crear una entidad de usuario de prueba"""
    from uuid import uuid4

    from apps.user_profile.domain.entities import UserEntity

    defaults = {"id": str(uuid4()), "email": email, "profile_picture": None}
    defaults.update(kwargs)

    return UserEntity(**defaults)
