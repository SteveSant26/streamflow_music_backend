from rest_framework import serializers

from apps.playlists.api.dtos.playlist_dtos import (
    AddSongToPlaylistRequestDTO,
    PlaylistCreateRequestDTO,
    PlaylistResponseDTO,
    PlaylistSongResponseDTO,
    PlaylistUpdateRequestDTO,
)
from apps.playlists.api.mappers.playlist_mapper import PlaylistMapper
from common.serializers.base_entity_serializer import BaseEntitySerializer


class PlaylistCreateSerializer(BaseEntitySerializer):
    """Serializer para crear playlists"""
    
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    is_public = serializers.BooleanField(default=False)
    
    mapper_class = PlaylistMapper()
    expected_dto_type = PlaylistCreateRequestDTO
    
    class Meta:
        fields = ["name", "description", "is_public"]
    
    def to_dto(self, validated_data):
        return PlaylistCreateRequestDTO(
            name=validated_data["name"],
            description=validated_data.get("description"),
            is_public=validated_data.get("is_public", False),
        )


class PlaylistUpdateSerializer(BaseEntitySerializer):
    """Serializer para actualizar playlists"""
    
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    is_public = serializers.BooleanField(required=False)
    
    mapper_class = PlaylistMapper()
    expected_dto_type = PlaylistUpdateRequestDTO
    
    class Meta:
        fields = ["name", "description", "is_public"]
    
    def to_dto(self, validated_data):
        return PlaylistUpdateRequestDTO(
            name=validated_data.get("name"),
            description=validated_data.get("description"),
            is_public=validated_data.get("is_public"),
        )


class PlaylistSongResponseSerializer(BaseEntitySerializer):
    """Serializer para canciones en playlists"""
    
    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField(read_only=True)
    artist_name = serializers.CharField(read_only=True, allow_null=True)
    album_name = serializers.CharField(read_only=True, allow_null=True)
    duration_seconds = serializers.IntegerField(read_only=True)
    thumbnail_url = serializers.URLField(read_only=True, allow_null=True)
    position = serializers.IntegerField(read_only=True)
    added_at = serializers.DateTimeField(read_only=True)
    
    mapper_class = PlaylistMapper()
    expected_dto_type = PlaylistSongResponseDTO
    
    class Meta:
        fields = [
            "id", "title", "artist_name", "album_name", 
            "duration_seconds", "thumbnail_url", "position", "added_at"
        ]


class PlaylistResponseSerializer(BaseEntitySerializer):
    """Serializer para respuesta de playlists"""
    
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    user_id = serializers.UUIDField(read_only=True)
    is_default = serializers.BooleanField(read_only=True)
    is_public = serializers.BooleanField(read_only=True)
    total_songs = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)
    songs = PlaylistSongResponseSerializer(many=True, read_only=True, required=False)
    
    mapper_class = PlaylistMapper()
    expected_dto_type = PlaylistResponseDTO
    
    class Meta:
        fields = [
            "id", "name", "description", "user_id", "is_default", 
            "is_public", "total_songs", "created_at", "updated_at", "songs"
        ]


class AddSongToPlaylistSerializer(BaseEntitySerializer):
    """Serializer para agregar canciones a playlists"""
    
    song_id = serializers.UUIDField()
    position = serializers.IntegerField(required=False, min_value=1)
    
    mapper_class = PlaylistMapper()
    expected_dto_type = AddSongToPlaylistRequestDTO
    
    class Meta:
        fields = ["song_id", "position"]
    
    def to_dto(self, validated_data):
        return AddSongToPlaylistRequestDTO(
            song_id=validated_data["song_id"],
            position=validated_data.get("position"),
        )
