from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .simple_views import TestView, test_function_view
from .viewsets import SongViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r"", SongViewSet, basename="songs")

app_name = "songs"

urlpatterns = [
    # ViewSets con DRF Router - directamente sin 'api/' extra
    path("", include(router.urls)),
    # Vistas de prueba legacy (considera eliminarlas en producción)
    path("test/", TestView.as_view(), name="test"),
    path("test-function/", test_function_view, name="test-function"),
]
