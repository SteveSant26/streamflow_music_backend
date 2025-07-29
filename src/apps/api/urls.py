from django.urls import include, path
from django.http import JsonResponse

# Vista simple para probar la conexión
def test_connection(request):
    return JsonResponse({
        'status': 'success',
        'message': '🎉 Django backend funcionando correctamente!',
        'django_version': '5.2.4',
        'endpoints': [
            'GET /api/test/',
            'GET /api/user/',
        ]
    })

urlpatterns = [
    path("test/", test_connection, name="test_connection"),
    path("user/", include("apps.user_profile.api.urls")),
]
