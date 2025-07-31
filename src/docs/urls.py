from django.conf import settings
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .schema import SupabaseAuthenticationScheme  # noqa: F401

urlpatterns = []

if settings.DEBUG:
    urlpatterns += [
        # Esquema en formato OpenAPI JSON
        path("schema/", SpectacularAPIView.as_view(), name="schema"),
        # Swagger UI
        path(
            "swagger/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        # Redoc UI
        path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
