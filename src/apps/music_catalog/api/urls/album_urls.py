from django.urls import path

from ..views.album_views import (
    get_album_detail,
    get_albums_by_artist,
    get_albums_by_genre,
    get_all_albums,
    get_popular_albums,
    get_recent_albums,
)

urlpatterns = [
    path("", get_all_albums, name="get_all_albums"),
    path("<str:album_id>/", get_album_detail, name="get_album_detail"),
    path("popular/", get_popular_albums, name="get_popular_albums"),
    path("recent/", get_recent_albums, name="get_recent_albums"),
    path("artist/<str:artist_id>/", get_albums_by_artist, name="get_albums_by_artist"),
    path("genre/<str:genre_id>/", get_albums_by_genre, name="get_albums_by_genre"),
]
