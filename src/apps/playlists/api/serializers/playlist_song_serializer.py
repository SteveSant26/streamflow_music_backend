from rest_framework import serializers

from apps.playlists.api.dtos import PlaylistSongResponseDTO
from apps.playlists.domain.entities import PlaylistSongEntity
from common.serializers.base_entity_serializer import BaseEntitySerializer


class PlaylistSongResponseSerializer(BaseEntitySerializer):
    """Serializer para canciones en playlists"""

    # Configuración para el serializer base
    mapper_class = (
        None  # PlaylistSongMapper tiene problemas de implementación abstracta
    )
    entity_class = PlaylistSongEntity
    dto_class = PlaylistSongResponseDTO

    id = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    artist_name = serializers.CharField(read_only=True, allow_null=True)
    album_name = serializers.CharField(read_only=True, allow_null=True)
    duration_seconds = serializers.IntegerField(read_only=True)
    thumbnail_url = serializers.URLField(read_only=True, allow_null=True)
    position = serializers.IntegerField(read_only=True)
    added_at = serializers.DateTimeField(read_only=True)

    class Meta:
        fields = [
            "id",
            "title",
            "artist_name",
            "album_name",
            "duration_seconds",
            "thumbnail_url",
            "position",
            "added_at",
        ]
