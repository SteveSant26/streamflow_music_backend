from django.urls import include, path

app_name = "music_catalog"

urlpatterns = [
    # Incluir URLs específicas por entidad
    path("songs/", include("apps.music_catalog.api.urls.song_urls")),
    path("artists/", include("apps.music_catalog.api.urls.artist_urls")),
    path("albums/", include("apps.music_catalog.api.urls.album_urls")),
    path("genres/", include("apps.music_catalog.api.urls.genre_urls")),
    path("search/", include("apps.music_catalog.api.urls.search_urls")),
]
