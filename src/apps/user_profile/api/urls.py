from rest_framework.routers import DefaultRouter
from django.urls import path
from django.http import JsonResponse
from ..infrastructure.models.user_profile import UserProfile

from .views import UserProfileViewSet

# Vista pública para probar user profiles
def test_user_profiles(request):
    try:
        # Obtener algunos perfiles (datos públicos solamente)
        profiles = UserProfile.objects.all()[:10]
        
        profiles_data = []
        for profile in profiles:
            profiles_data.append({
                'id': str(profile.id),
                'email': profile.email,
                'profile_picture': profile.profile_picture,
                'has_picture': bool(profile.profile_picture)
            })
        
        return JsonResponse({
            'status': 'success',
            'total_profiles': UserProfile.objects.count(),
            'profiles': profiles_data,
            'message': f'📊 {len(profiles_data)} perfiles encontrados'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }, status=500)

router = DefaultRouter()
router.register(r"profile", UserProfileViewSet, basename="user-profile")

urlpatterns = [
    path("test-profiles/", test_user_profiles, name="test_user_profiles"),
] + router.urls
