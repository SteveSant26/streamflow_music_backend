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
    "import_export",
    "corsheaders",
    "drf_yasg",
    "django_filters",
]
LOCAL_APPS = [
    "api",
]
INSTALLED_APPS = THEME_APPLICATION + DEFAULT_DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

SWAGGER_SETTINGS = {
    "DOC_EXPANSION": "none",
}
