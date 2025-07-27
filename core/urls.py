from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("docs/", include("docs.urls")),
    path("", include("api.urls")),
]
