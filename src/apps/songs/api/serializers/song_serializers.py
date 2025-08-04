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


class SearchRequestSerializer(serializers.Serializer):
    """Serializer para requests de búsqueda"""

    query = serializers.CharField(max_length=255, required=True)
    limit = serializers.IntegerField(min_value=1, max_value=50, default=20)
    include_youtube = serializers.BooleanField(default=True)


class RandomSongsRequestSerializer(serializers.Serializer):
    """Serializer para requests de canciones aleatorias"""

    count = serializers.IntegerField(min_value=1, max_value=20, default=6)
    force_refresh = serializers.BooleanField(default=False)


class ProcessVideoRequestSerializer(serializers.Serializer):
    """Serializer para procesar un video específico de YouTube"""

    video_id = serializers.CharField(max_length=20, required=True)

    def validate_video_id(self, value):
        """Valida el formato del video ID"""
        import re

        if not re.match(r"^[a-zA-Z0-9_-]{11}$", value):
            raise serializers.ValidationError("Invalid YouTube video ID format")
        return value


class SongStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de canciones"""

    total_songs = serializers.IntegerField()
    total_artists = serializers.IntegerField()
    total_play_count = serializers.IntegerField()
    songs_with_audio = serializers.IntegerField()
    most_played_song = SongListSerializer(allow_null=True)
    recent_songs = SongListSerializer(many=True)
