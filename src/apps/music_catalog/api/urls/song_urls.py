from django.urls import path

from ..views.song_views import (
    get_all_songs,
    get_popular_songs,
    get_song_detail,
    get_songs_by_album,
    get_songs_by_artist,
    get_songs_by_genre,
    play_song,
)

urlpatterns = [
    path("", get_all_songs, name="get_all_songs"),
    path("<str:song_id>/", get_song_detail, name="get_song_detail"),
    path("play/", play_song, name="play_song"),
    path("popular/", get_popular_songs, name="get_popular_songs"),
    path("artist/<str:artist_id>/", get_songs_by_artist, name="get_songs_by_artist"),
    path("album/<str:album_id>/", get_songs_by_album, name="get_songs_by_album"),
    path("genre/<str:genre_id>/", get_songs_by_genre, name="get_songs_by_genre"),
]
