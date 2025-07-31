from django.urls import path

from ..views.artist_views import (
    get_all_artists,
    get_artist_detail,
    get_artists_by_genre,
    get_popular_artists,
)

urlpatterns = [
    path("", get_all_artists, name="get_all_artists"),
    path("<str:artist_id>/", get_artist_detail, name="get_artist_detail"),
    path("popular/", get_popular_artists, name="get_popular_artists"),
    path("genre/<str:genre_id>/", get_artists_by_genre, name="get_artists_by_genre"),
]
