from rest_framework import serializers

from apps.playlists.api.dtos import AddSongToPlaylistRequestDTO
from common.serializers.base_entity_serializer import BaseEntitySerializer


class AddSongToPlaylistSerializer(BaseEntitySerializer):
    """Serializer para agregar canciones a playlists"""

    # Configuración para el serializer base
    mapper_class = None  # No necesita mapper para operaciones de request
    entity_class = None
    dto_class = AddSongToPlaylistRequestDTO

    song_id = serializers.UUIDField()
    position = serializers.IntegerField(required=False, min_value=1)

    class Meta:
        fields = ["song_id", "position"]

    def to_dto(self, validated_data):
        return AddSongToPlaylistRequestDTO(
            playlist_id="",  # Se asigna en la vista
            song_id=validated_data["song_id"],
            position=validated_data.get("position"),
        )
