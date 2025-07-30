from django.urls import include, path

urlpatterns = [
    path("user/", include("apps.user_profile.api.urls")),
    path("music/", include("apps.music_catalog.api.urls")),
]
