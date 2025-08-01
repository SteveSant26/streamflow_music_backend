import os

from src.common.utils import LoggingConfig

from .apps_settings import INSTALLED_APPS, SPECTACULAR_SETTINGS  # noqa: F401
from .auth_settings import AUTH_PASSWORD_VALIDATORS  # noqa: F401
from .test_database_settings import DATABASES  # noqa: F401
from .jazzmin_settings import JAZZMIN_SETTINGS, JAZZMIN_UI_TWEAKS  # noqa: F401
from .middleware_settings import MIDDLEWARE  # noqa: F401
from .rest_framework_settings import REST_FRAMEWORK  # noqa: F401
from .supabase_settings import (  # noqa: F401
    SUPABASE_ANON_KEY,
    SUPABASE_JWT_ALGORITHM,
    SUPABASE_JWT_SECRET,
    SUPABASE_PROJECT_ID,
    SUPABASE_SERVICE_KEY,
    SUPABASE_URL,
)
from .templates_settings import TEMPLATES  # noqa: F401
from .utils.env import BASE_DIR, ENVIRONMENT, env
from .youtube_settings import (  # noqa: F401
    RANDOM_MUSIC_QUERIES,
    YOUTUBE_API_KEY,
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    YOUTUBE_CATEGORIES,
    YT_DLP_AUDIO_OPTS,
)

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# CORS Settings
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")

# Configuraciones adicionales de CORS para desarrollo
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOWED_HEADERS = [
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
    ]

# Deshabilitar APPEND_SLASH para APIs
APPEND_SLASH = False

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
