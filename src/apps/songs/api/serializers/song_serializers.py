from rest_framework import serializers

from apps.songs.api.dtos import SongResponseDTO
from apps.songs.api.mappers import SongMapper
from apps.songs.domain.entities import SongEntity
from common.serializers import BaseEntitySerializer


class SongSerializer(BaseEntitySerializer):
    """Serializer para canciones"""

    # Configuración para el serializer base
    mapper_class = SongMapper()
    entity_class = SongEntity
    dto_class = SongResponseDTO

    # Campos adicionales calculados
    duration_formatted = serializers.SerializerMethodField()
    genre_names_display = serializers.SerializerMethodField()

    def get_duration_formatted(self, obj) -> str:
        """Retorna la duración en formato MM:SS"""
        return obj.duration_formatted

    def get_genre_names_display(self, obj) -> str:
        """Retorna los nombres de géneros como string separado por comas"""
        if hasattr(obj, "genre_names") and obj.genre_names:
            return ", ".join(obj.genre_names)
        return "Sin género"


class SongListSerializer(BaseEntitySerializer):
    """Serializer simplificado para listas de canciones"""

    # Configuración para el serializer base
    mapper_class = SongMapper()
    entity_class = SongEntity
    dto_class = SongResponseDTO

    # Campos adicionales calculados
    duration_formatted = serializers.SerializerMethodField()
    genre_names_display = serializers.SerializerMethodField()

    def get_duration_formatted(self, obj) -> str:
        """Retorna la duración en formato MM:SS"""
        return obj.duration_formatted

    def get_genre_names_display(self, obj) -> str:
        """Retorna los nombres de géneros como string separado por comas"""
        if hasattr(obj, "genre_names") and obj.genre_names:
            return ", ".join(obj.genre_names)
        return "Sin género"
