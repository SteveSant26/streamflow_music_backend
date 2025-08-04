from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def home_view(request):
    """Vista simple para la página de inicio"""
    return JsonResponse(
        {
            "message": "StreamFlow Music Backend API",
            "status": "Running",
            "version": "1.0.0",
            "available_endpoints": {
                "admin": "/admin/",
                "docs": "/docs/",
                "api_test": "/api/test/",
                "auth_register": "/api/auth/register/",
                "auth_login": "/api/auth/login/",
                "user_profiles": "/api/user/test-profiles/",
            },
        }
    )


urlpatterns = [
    path("", home_view, name="home"),  # Página de inicio
    path("admin/", admin.site.urls),
    # Temporalmente comentado para evitar importación circular
    # path("docs/", include("docs.urls")),
    path("api/", include("api.urls")),
]
