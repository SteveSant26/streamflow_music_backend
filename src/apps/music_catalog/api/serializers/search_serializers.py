from rest_framework import serializers

from .album_serializers import AlbumSerializer
from .artist_serializers import ArtistSerializer
from .genre_serializers import GenreSerializer
from .song_serializers import SongSerializer


class SearchResultSerializer(serializers.Serializer):
    """Serializer para resultados de búsqueda"""

    query = serializers.CharField()
    songs = SongSerializer(many=True)
    artists = ArtistSerializer(many=True)
    albums = AlbumSerializer(many=True)
    genres = GenreSerializer(many=True)
    total_results = serializers.IntegerField()


class PaginatedResultSerializer(serializers.Serializer):
    """Serializer para resultados paginados"""

    results = serializers.ListField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_items = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()
