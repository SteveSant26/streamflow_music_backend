from django.urls import path

from .views import (
<<<<<<< HEAD
    MostPopularSongsView,
    RandomSongsView,
    SearchSongsView,
    SongDetailView,
    increment_play_count_view,
)

urlpatterns = [
    # Búsqueda de canciones
    path("search/", SearchSongsView.as_view(), name="search-songs"),
=======
    IncrementPlayCountAPIView,
    MostPopularSongsView,
    RandomSongsView,
    SongViewSet,
)

# Router para el ViewSet
router = DefaultRouter()
router.register(r"list", SongViewSet, basename="songs-viewset")

urlpatterns = [
    # ViewSet para listado y detalle con filtros (incluye búsqueda unificada con YouTube)
    path("", include(router.urls)),
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
    # Canciones aleatorias
    path("random/", RandomSongsView.as_view(), name="random-songs"),
    # Canciones más populares
    path("most-popular/", MostPopularSongsView.as_view(), name="most-popular-songs"),
<<<<<<< HEAD
    # Detalles de una canción específica
    path("<uuid:song_id>/", SongDetailView.as_view(), name="song-detail"),
    # Incrementar contador de reproducciones
    path(
        "<uuid:song_id>/increment-play-count/",
        increment_play_count_view,
        name="increment-play-count",
=======
    # Nueva vista API para incrementar contador (más consistente)
    path(
        "api/<uuid:song_id>/increment-play-count/",
        IncrementPlayCountAPIView.as_view(),
        name="increment-play-count-api",
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
    ),
]
