from django.urls import path
from .views import (
    UserStatisticsView,
    UserTopContentView,
    GlobalStatisticsView,
    TrendingContentView,
    TopArtistsView,
    TopSongsView,
    RecordPlayView,
    ToggleFavoriteArtistView,
    ToggleFavoriteSongView
)

app_name = 'statistics'

urlpatterns = [
    # Estadísticas del usuario
    path('user/', UserStatisticsView.as_view(), name='user-statistics'),
    path('user/top/', UserTopContentView.as_view(), name='user-top-content'),
    
    # Estadísticas globales
    path('global/', GlobalStatisticsView.as_view(), name='global-statistics'),
    path('trending/', TrendingContentView.as_view(), name='trending-content'),
    
    # Top charts
    path('top/artists/', TopArtistsView.as_view(), name='top-artists'),
    path('top/songs/', TopSongsView.as_view(), name='top-songs'),
    
    # Acciones del usuario
    path('play/', RecordPlayView.as_view(), name='record-play'),
    path('favorite/artist/', ToggleFavoriteArtistView.as_view(), name='toggle-favorite-artist'),
    path('favorite/song/', ToggleFavoriteSongView.as_view(), name='toggle-favorite-song'),
]
