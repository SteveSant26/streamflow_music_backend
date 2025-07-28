import os

from src.common.utils import LoggingConfig

from .apps_settings import INSTALLED_APPS, SWAGGER_SETTINGS  # noqa: F401
from .auth_settings import AUTH_PASSWORD_VALIDATORS  # noqa: F401
from .database_settings import DATABASES  # noqa: F401
from .jazzmin_settings import JAZZMIN_SETTINGS, JAZZMIN_UI_TWEAKS  # noqa: F401
from .middleware_settings import MIDDLEWARE  # noqa: F401
from .rest_framework_settings import REST_FRAMEWORK  # noqa: F401
from .supabase_settings import SUPABASE_ANON_KEY  # noqa: F401
from .supabase_settings import SUPABASE_JWT_ALGORITHM  # noqa: F401
from .supabase_settings import SUPABASE_JWT_SECRET  # noqa: F401
from .supabase_settings import SUPABASE_PROJECT_ID  # noqa: F401
from .supabase_settings import SUPABASE_SERVICE_KEY  # noqa: F401
from .templates_settings import TEMPLATES  # noqa: F401
from .utils.env import BASE_DIR, ENVIRONMENT, env

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = LoggingConfig.get_logging_config(bool(DEBUG), ENVIRONMENT)

if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
