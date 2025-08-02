from django.urls import path

from apps.songs.api.views import (
    ProcessYouTubeVideoView,
    RandomSongsView,
    SearchSongsView,
    SongDetailView,
    increment_play_count_view,
)

urlpatterns = [
    # Búsqueda de canciones
    path("search/", SearchSongsView.as_view(), name="search-songs"),
    # Canciones aleatorias
    path("random/", RandomSongsView.as_view(), name="random-songs"),
    # Detalles de una canción específica
    path("<uuid:song_id>/", SongDetailView.as_view(), name="song-detail"),
    # Procesar video de YouTube
    path(
        "process-youtube/",
        ProcessYouTubeVideoView.as_view(),
        name="process-youtube-video",
    ),
    # Incrementar contador de reproducciones
    path(
        "<uuid:song_id>/increment-play-count/",
        increment_play_count_view,
        name="increment-play-count",
    ),
]
