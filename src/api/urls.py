from django.urls import include, path

urlpatterns = [
    path("user/", include("apps.user_profile.api.urls")),
    path("artists/", include("apps.artists.api.urls")),
    path("albums/", include("apps.albums.api.urls")),
    path("songs/", include("apps.songs.api.urls")),
    path("genres/", include("apps.genres.api.urls")),
<<<<<<< HEAD
    # path("search/", include("apps.music_search.api.urls")),
    # path("payments/", include(" apps.payments.api.urls")),  # Temporarily disabled
=======
    path("playlists/", include("apps.playlists.api.urls")),
    path("payments/", include("apps.payments.api.urls")),
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
]
