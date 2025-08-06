from rest_framework import serializers

from apps.playlists.api.dtos import (
    CreatePlaylistRequestDTO,
    PlaylistResponseDTO,
    UpdatePlaylistRequestDTO,
)
from apps.playlists.api.mappers import PlaylistMapper
from apps.playlists.domain.entities import PlaylistEntity
from common.serializers.base_entity_serializer import BaseEntitySerializer

from .playlist_song_serializer import PlaylistSongResponseSerializer


class PlaylistCreateSerializer(BaseEntitySerializer):
    """Serializer para crear playlists"""

    # Configuración para el serializer base
    mapper_class = None  # No necesita mapper para crear
    entity_class = None
    dto_class = CreatePlaylistRequestDTO

    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    is_public = serializers.BooleanField(default=False)

    class Meta:
        fields = ["name", "description", "is_public"]

    def to_dto(self, validated_data):
        """Convierte datos validados a DTO"""
        return CreatePlaylistRequestDTO(
            name=validated_data["name"],
            description=validated_data.get("description"),
            is_public=validated_data.get("is_public", False),
        )


class PlaylistUpdateSerializer(BaseEntitySerializer):
    """Serializer para actualizar playlists"""

    # Configuración para el serializer base
    mapper_class = None  # No necesita mapper para actualizar
    entity_class = None
    dto_class = UpdatePlaylistRequestDTO

    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    is_public = serializers.BooleanField(required=False)

    class Meta:
        fields = ["name", "description", "is_public"]

    def to_dto(self, validated_data):
        """Convierte datos validados a DTO"""
        return UpdatePlaylistRequestDTO(
            playlist_id="",  # Se asigna en la vista
            name=validated_data.get("name"),
            description=validated_data.get("description"),
            is_public=validated_data.get("is_public"),
        )


class PlaylistResponseSerializer(BaseEntitySerializer):
    """Serializer para respuesta de playlists"""

    # Configuración para el serializer base
    mapper_class = PlaylistMapper()
    entity_class = PlaylistEntity
    dto_class = PlaylistResponseDTO

    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    user_id = serializers.CharField(read_only=True)
    is_default = serializers.BooleanField(read_only=True)
    is_public = serializers.BooleanField(read_only=True)
    total_songs = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)
    songs = PlaylistSongResponseSerializer(many=True, read_only=True, required=False)

    class Meta:
        fields = [
            "id",
            "name",
            "description",
            "user_id",
            "is_default",
            "is_public",
            "total_songs",
            "created_at",
            "updated_at",
            "songs",
        ]
