from django.urls import include, path

urlpatterns = [
    path("user/", include("apps.user_profile.api.urls")),
    path("artists/", include("apps.artists.api.urls")),
    path("albums/", include("apps.albums.api.urls")),
    path("songs/", include("apps.songs.api.urls")),
    path("genres/", include("apps.genres.api.urls")),
    # path("search/", include("apps.music_search.api.urls")),
    # path("payments/", include(" apps.payments.api.urls")),  # Temporarily disabled
]
