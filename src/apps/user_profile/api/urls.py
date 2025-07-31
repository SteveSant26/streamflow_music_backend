from django.http import JsonResponse
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import UserProfileViewSet


def test_profiles_endpoint(request):
    """Endpoint de prueba para test-profiles"""
    return JsonResponse(
        {
            "message": "Endpoint test-profiles funcionando",
            "status": "OK",
            "available_profiles": [],
        }
    )


router = DefaultRouter()

router.register(r"profile", UserProfileViewSet)

urlpatterns = [
    path("test-profiles/", test_profiles_endpoint, name="test-profiles"),
] + router.urls
