from django.urls import include, path

urlpatterns = [
    path("user/", include("apps.user_profile.api.urls"), name="user_profile"),
    path("music/", include("apps.music_catalog.api.urls")),
]
