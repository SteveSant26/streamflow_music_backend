from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    MostPopularSongsView,
    RandomSongsView,
    SearchSongsView,
    SongDetailView,
    SongViewSet,
    increment_play_count_view,
)

# Router para el ViewSet
router = DefaultRouter()
router.register(r"", SongViewSet, basename="songs")

urlpatterns = [
    # ViewSet para listado y detalle con filtros
    path("", include(router.urls)),
    # Búsqueda de canciones
    path("search/", SearchSongsView.as_view(), name="search-songs"),
    # Canciones aleatorias
    path("random/", RandomSongsView.as_view(), name="random-songs"),
    # Canciones más populares
    path("most-popular/", MostPopularSongsView.as_view(), name="most-popular-songs"),
    path("<uuid:song_id>/", SongDetailView.as_view(), name="song-detail"),
    # Incrementar contador de reproducciones
    path(
        "<uuid:song_id>/increment-play-count/",
        increment_play_count_view,
        name="increment-play-count",
    ),
]
