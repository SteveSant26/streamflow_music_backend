import os

from src.common.utils import LoggingConfig

from .utils.env import BASE_DIR, ENVIRONMENT, env

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")

ROOT_URLCONF = "core.urls"

WSGI_APPLICATION = "core.wsgi.application"

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = LoggingConfig.get_logging_config(DEBUG, ENVIRONMENT)

if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
