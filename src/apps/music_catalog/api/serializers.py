from rest_framework import serializers
from apps.music_catalog.domain.entities import (
    SongEntity,
    ArtistEntity, 
    AlbumEntity,
    GenreEntity,
    SearchResultEntity,
    PaginatedResultEntity
)


class GenreSerializer(serializers.Serializer):
    """Serializer para entidad de género"""
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    song_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ArtistSerializer(serializers.Serializer):
    """Serializer para entidad de artista"""
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    biography = serializers.CharField(required=False, allow_blank=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    followers_count = serializers.IntegerField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class AlbumSerializer(serializers.Serializer):
    """Serializer para entidad de álbum"""
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=200)
    artist_id = serializers.CharField()
    artist_name = serializers.CharField(read_only=True)
    release_date = serializers.DateField()
    description = serializers.CharField(required=False, allow_blank=True)
    cover_image_url = serializers.URLField(required=False, allow_blank=True)
    total_tracks = serializers.IntegerField(read_only=True)
    play_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class SongSerializer(serializers.Serializer):
    """Serializer para entidad de canción"""
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=200)
    artist_id = serializers.CharField()
    artist_name = serializers.CharField(read_only=True)
    album_id = serializers.CharField(required=False, allow_null=True)
    album_title = serializers.CharField(read_only=True, required=False)
    duration_seconds = serializers.IntegerField()
    file_url = serializers.URLField()
    lyrics = serializers.CharField(required=False, allow_blank=True)
    track_number = serializers.IntegerField(required=False)
    genre_id = serializers.CharField(required=False, allow_null=True)
    genre_name = serializers.CharField(read_only=True, required=False)
    play_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class SongDetailSerializer(SongSerializer):
    """Serializer detallado para canción con información completa"""
    pass


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


# Serializers para requests
class PlaySongRequestSerializer(serializers.Serializer):
    """Serializer para request de reproducir canción"""
    song_id = serializers.CharField()


class SearchRequestSerializer(serializers.Serializer):
    """Serializer para request de búsqueda"""
    query = serializers.CharField(max_length=200)
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)


class FilterSearchRequestSerializer(serializers.Serializer):
    """Serializer para búsqueda con filtros"""
    genre_id = serializers.CharField(required=False, allow_blank=True)
    artist_id = serializers.CharField(required=False, allow_blank=True)
    album_id = serializers.CharField(required=False, allow_blank=True)
    year = serializers.IntegerField(required=False, min_value=1900, max_value=2100)
    duration_min = serializers.IntegerField(required=False, min_value=0)  # en minutos
    duration_max = serializers.IntegerField(required=False, min_value=0)  # en minutos
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)
