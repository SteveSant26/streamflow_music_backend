THEME_APPLICATION = [
    "jazzmin",
]
DEFAULT_DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "import_export",
    "corsheaders",
    "drf_yasg",
    "django_filters",
]
LOCAL_APPS = [
    "apps.user_profile",
]
INSTALLED_APPS = THEME_APPLICATION + DEFAULT_DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

SWAGGER_SETTINGS = {
    "DOC_EXPANSION": "none",
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer <token>'",
        },
    },
    "USE_SESSION_AUTH": False,
}
