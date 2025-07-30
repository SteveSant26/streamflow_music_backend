from rest_framework.routers import DefaultRouter
from django.urls import path
from django.http import JsonResponse

from .views import UserProfileViewSet

def test_profiles_endpoint(request):
    """Endpoint de prueba para test-profiles"""
    return JsonResponse({
        'message': 'Endpoint test-profiles funcionando',
        'status': 'OK',
        'available_profiles': []
    })

router = DefaultRouter()

router.register(r"profile", UserProfileViewSet, basename="user-profile")

urlpatterns = [
    path("test-profiles/", test_profiles_endpoint, name="test-profiles"),
] + router.urls
