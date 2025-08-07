from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IncrementPlayCountAPIView,
    MostPopularSongsView,
    RandomSongsView,
    SongViewSet,
)
from .views.lyrics_viewset import LyricsView

# Router para el ViewSet
router = DefaultRouter()
router.register(r"list", SongViewSet, basename="songs-viewset")

urlpatterns = [
    # ViewSet para listado y detalle con filtros (incluye búsqueda unificada con YouTube)
    path("", include(router.urls)),
    # Canciones aleatorias
    path("random/", RandomSongsView.as_view(), name="random-songs"),
    # Canciones más populares
    path("most-popular/", MostPopularSongsView.as_view(), name="most-popular-songs"),
    # Nueva vista API para incrementar contador (más consistente)
    path(
        "<uuid:song_id>/increment-play-count/",
        IncrementPlayCountAPIView.as_view(),
        name="increment-play-count",
    ),
    path(
        "<uuid:song_id>/lyrics/",
        LyricsView.as_view(),
        name="get-lyrics",
    ),
]
