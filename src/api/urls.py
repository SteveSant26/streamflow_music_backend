from django.urls import include, path

urlpatterns = [
    path("user/", include("apps.user_profile.api.urls")),
    path("artists/", include("apps.artists.api.urls")),
    path("albums/", include("apps.albums.api.urls")),
    path("songs/", include("apps.songs.api.urls")),
    path("genres/", include("apps.genres.api.urls")),
    path("playlists/", include("apps.playlists.api.urls")),
    path("favorites/", include("apps.favorites.urls")),
    # path("payments    /", include(" apps.payments.api.urls")),  # Temporarily disabled
]
