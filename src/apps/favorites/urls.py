from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FavoriteSongViewSet, FavoriteArtistViewSet, FavoriteAlbumViewSet

# Router para los ViewSets
router = DefaultRouter()
router.register(r'songs', FavoriteSongViewSet, basename='favorite-songs')
router.register(r'artists', FavoriteArtistViewSet, basename='favorite-artists')
router.register(r'albums', FavoriteAlbumViewSet, basename='favorite-albums')

urlpatterns = [
    path('', include(router.urls)),
]
