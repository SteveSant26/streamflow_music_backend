import os
from pathlib import Path

from environ import Env

from src.common.utils import LoggingConfig

BASE_DIR = Path(__file__).resolve().parent.parent


ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")


env = Env()
env_file = BASE_DIR / f".env.{ENVIRONMENT}"
env.read_env(env_file)


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
