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
    "drf_spectacular",
    "django_filters",
]
LOCAL_APPS = [
    "apps.user_profile",
    "apps.artists",
    "apps.albums",
    "apps.songs",
    "apps.genres",
    "apps.music_search",
    "apps.payments",
    "apps.playlists",
]

INSTALLED_APPS = THEME_APPLICATION + DEFAULT_DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


SPECTACULAR_SETTINGS = {
    "TITLE": "StreamFlow Music API",
    "DESCRIPTION": "Documentación de la API de StreamFlow Music con autenticación Supabase",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SECURITY": [{"BearerAuth": []}],  # ← hace que se aplique por defecto
    "COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",  # opcional pero útil para claridad
            }
        }
    },
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,  # Mantiene el token después de refrescar
        "displayOperationId": False,
        "filter": True,  # Permite filtrar endpoints
        "tryItOutEnabled": True,  # Habilita el botón "Try it out"
        "supportedSubmitMethods": [
            "get",
            "post",
            "put",
            "delete",
            "patch",
        ],  # Métodos soportados
        "requestInterceptor": "(request) => { if (request.headers.Authorization) { request.headers.Authorization = request.headers.Authorization; } return request; }",  # noqa
    },
}
