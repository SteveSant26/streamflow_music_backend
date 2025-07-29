from django.urls import include, path
from django.http import JsonResponse
from apps.user_profile.infrastructure.models.user_profile import UserProfile

# Vista simple para probar la conexión
def test_connection(request):
    return JsonResponse({
        'status': 'success',
        'message': '🎉 Django backend funcionando correctamente!',
        'django_version': '5.2.4',
        'endpoints': [
            'GET /api/test/',
            'GET /api/test-users/',
            'GET /api/user/profile/',
        ]
    })

# Vista para probar user profiles sin autenticación
def test_users(request):
    try:
        # Contar usuarios
        user_count = UserProfile.objects.count()
        
        # Obtener algunos usuarios (sin datos sensibles)
        users = UserProfile.objects.all()[:5].values(
            'id', 'email', 'profile_picture'
        )
        
        return JsonResponse({
            'status': 'success',
            'user_count': user_count,
            'sample_users': list(users),
            'message': f'📊 Total de usuarios: {user_count}'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }, status=500)

urlpatterns = [
    path("test/", test_connection, name="test_connection"),
    path("test-users/", test_users, name="test_users"),
    path("user/", include("apps.user_profile.api.urls")),
]
