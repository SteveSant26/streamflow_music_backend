from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Streamflow Music API",
        default_version="v0.1",
        description="Esta es la documentacion de la API de Streamflow Music",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="tinocoloco265@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
