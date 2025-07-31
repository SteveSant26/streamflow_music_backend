from .album_views import *
from .artist_views import *
from .genre_views import *
from .search_views import *
from .song_views import *

__all__ = [
    # Song views
    "get_all_songs",
    "get_song_detail",
    "play_song",
    "get_popular_songs",
    "get_songs_by_artist",
    "get_songs_by_album",
    "get_songs_by_genre",
    # Artist views
    "get_all_artists",
    "get_artist_detail",
    "get_popular_artists",
    "get_artists_by_genre",
    # Album views
    "get_all_albums",
    "get_album_detail",
    "get_popular_albums",
    "get_albums_by_artist",
    "get_albums_by_genre",
    "get_recent_albums",
    # Genre views
    "get_all_genres",
    "get_genre_detail",
    # Search views
    "search_all",
    "search_songs",
    "search_artists",
    "search_albums",
    "advanced_search",
]
