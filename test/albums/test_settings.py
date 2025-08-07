"""
Configuración temporal para tests de modelos
"""

<<<<<<< HEAD
=======

>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
# Configuración temporal de Django solo para testing
SECRET_KEY = "test-secret-key-for-album-tests"
DEBUG = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = False
USE_I18N = False
