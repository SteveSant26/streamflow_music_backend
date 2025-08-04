from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.playlists.api.views import PlaylistViewSet, PlaylistSongViewSet

# Router para las APIs REST
router = DefaultRouter()
router.register(r'playlists', PlaylistViewSet, basename='playlist')
router.register(r'playlists', PlaylistSongViewSet, basename='playlist-songs')

urlpatterns = [
    path('', include(router.urls)),
]
