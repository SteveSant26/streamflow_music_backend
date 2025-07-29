from django.urls import include, path
from django.http import JsonResponse
from apps.user_profile.infrastructure.models.user_profile import UserProfile
from .auth_views import register_view, login_view, logout_view

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
            'POST /api/auth/register/',
            'POST /api/auth/login/',
            'POST /api/auth/logout/',
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
    
    # Endpoints de autenticación (con y sin slash final para mayor compatibilidad)
    path("auth/register", register_view, name="auth_register"),
    path("auth/register/", register_view, name="auth_register_slash"),
    path("auth/login", login_view, name="auth_login"),
    path("auth/login/", login_view, name="auth_login_slash"),
    path("auth/logout", logout_view, name="auth_logout"),
    path("auth/logout/", logout_view, name="auth_logout_slash"),
]
