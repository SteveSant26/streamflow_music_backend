from django.urls import path

from ..views.search_views import (
    advanced_search,
    search_albums,
    search_all,
    search_artists,
    search_songs,
)

urlpatterns = [
    path("", search_all, name="search_all"),
    path("songs/", search_songs, name="search_songs"),
    path("artists/", search_artists, name="search_artists"),
    path("albums/", search_albums, name="search_albums"),
    path("advanced/", advanced_search, name="advanced_search"),
]
