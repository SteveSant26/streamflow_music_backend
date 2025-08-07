from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.playlists.api.views import PlaylistSongViewSet, PlaylistViewSet

# Router para las APIs REST
router = DefaultRouter()
router.register(r"playlist", PlaylistViewSet, basename="playlist")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "playlist-songs/<uuid:pk>/songs/",
        PlaylistSongViewSet.as_view({"get": "list_songs", "post": "add_song"}),
        name="playlist-songs",
    ),
    path(
        "playlist-songs/<uuid:pk>/songs/<uuid:song_id>/",
        PlaylistSongViewSet.as_view({"delete": "remove_song"}),
        name="playlist-songs-delete",
    ),
]
