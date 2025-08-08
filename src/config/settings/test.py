"""
🔧 CONFIGURACIÓN DE DJANGO PARA TESTS
=====================================
Configuración mínima de Django para permitir que los tests se ejecuten
"""

# Base de datos en memoria para tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


# Desactivar migraciones para tests más rápidos
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Configuración mínima para tests
SECRET_KEY = "test-secret-key-for-tests-only"
DEBUG = True
TESTING = True

# Cache en memoria para tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Desactivar logging durante tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
    },
}

# Configuraciones para tests más rápidos
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Media files para tests
MEDIA_ROOT = "/tmp/test_media"
STATIC_ROOT = "/tmp/test_static"

# Desactivar autenticación externa para tests
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Configuración mínima de apps para tests
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "django_filters",
    # Apps del proyecto
    "apps.songs",
    "apps.albums",
    "apps.artists",
    "apps.genres",
    "apps.playlists",
    "apps.payments",
    "apps.user_profile",
    "apps.statistics",
]

# Configuración básica de REST Framework para tests
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Configuración de CORS para tests
CORS_ALLOW_ALL_ORIGINS = True
