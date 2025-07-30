from django.urls import path
from . import views

app_name = 'music_catalog'

urlpatterns = [
    # ========================
    # ENDPOINTS DE CANCIONES
    # ========================
    path('songs/', views.get_all_songs, name='get_all_songs'),
    path('songs/<str:song_id>/', views.get_song_detail, name='get_song_detail'),
    path('songs/play/', views.play_song, name='play_song'),
    path('songs/popular/', views.get_popular_songs, name='get_popular_songs'),
    path('songs/artist/<str:artist_id>/', views.get_songs_by_artist, name='get_songs_by_artist'),
    path('songs/album/<str:album_id>/', views.get_songs_by_album, name='get_songs_by_album'),
    path('songs/genre/<str:genre_id>/', views.get_songs_by_genre, name='get_songs_by_genre'),
    
    # ========================
    # ENDPOINTS DE ARTISTAS
    # ========================
    path('artists/', views.get_all_artists, name='get_all_artists'),
    path('artists/<str:artist_id>/', views.get_artist_detail, name='get_artist_detail'),
    path('artists/popular/', views.get_popular_artists, name='get_popular_artists'),
    
    # ========================
    # ENDPOINTS DE ÁLBUMES
    # ========================
    path('albums/', views.get_all_albums, name='get_all_albums'),
    path('albums/<str:album_id>/', views.get_album_detail, name='get_album_detail'),
    path('albums/artist/<str:artist_id>/', views.get_albums_by_artist, name='get_albums_by_artist'),
    path('albums/popular/', views.get_popular_albums, name='get_popular_albums'),
    
    # ========================
    # ENDPOINTS DE GÉNEROS
    # ========================
    path('genres/', views.get_all_genres, name='get_all_genres'),
    path('genres/<str:genre_id>/', views.get_genre_detail, name='get_genre_detail'),
    
    # ========================
    # ENDPOINTS DE BÚSQUEDA
    # ========================
    path('search/', views.search_all, name='search_all'),
    path('search/songs/', views.search_songs, name='search_songs'),
    path('search/filters/', views.search_with_filters, name='search_with_filters'),
]
