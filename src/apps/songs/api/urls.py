from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IncrementPlayCountAPIView,
    MostPopularSongsView,
    RandomSongsView,
    SearchSongsView,
    SongDetailView,
    SongViewSet,
)

# Router para el ViewSet
router = DefaultRouter()
router.register(r"list", SongViewSet, basename="songs-viewset")

urlpatterns = [
    # ViewSet para listado y detalle con filtros
    path("", include(router.urls)),
    # Búsqueda de canciones
    path("search/", SearchSongsView.as_view(), name="search-songs"),
    # Canciones aleatorias
    path("random/", RandomSongsView.as_view(), name="random-songs"),
    # Canciones más populares
    path("most-popular/", MostPopularSongsView.as_view(), name="most-popular-songs"),
    path("detail/<uuid:song_id>/", SongDetailView.as_view(), name="song-detail"),
    # Nueva vista API para incrementar contador (más consistente)
    path(
        "api/<uuid:song_id>/increment-play-count/",
        IncrementPlayCountAPIView.as_view(),
        name="increment-play-count-api",
    ),
]
