from rest_framework import serializers

from apps.albums.api.mappers import AlbumMapper
from apps.albums.domain.entities import AlbumEntity
from common.serializers import BaseEntitySerializer

from ..dtos import AlbumResponseDTO


class AlbumSerializer(BaseEntitySerializer):
    """
    Serializer inteligente que hereda funcionalidad automática de conversión.
    Solo necesita definir las clases correspondientes.
    """

    # Configuración para el serializer base
    mapper_class = AlbumMapper()
    entity_class = AlbumEntity
    dto_class = AlbumResponseDTO

    # Definición de campos (opcional, solo para documentación/validación)
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    artist_id = serializers.CharField(read_only=True)
    artist_name = serializers.CharField(read_only=True)
    release_date = serializers.DateField(read_only=True, allow_null=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    cover_image_url = serializers.URLField(read_only=True, allow_null=True)
    total_tracks = serializers.IntegerField(read_only=True)
    play_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)


class AlbumSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de álbumes"""

    q = serializers.CharField(max_length=255, help_text="Texto de búsqueda")
    artist_id = serializers.UUIDField(
        required=False, help_text="ID del artista (opcional)"
    )
    artist_name = serializers.CharField(
        max_length=200, required=False, help_text="Nombre del artista (opcional)"
    )


class AlbumSearchResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de búsqueda de álbumes"""

    source = serializers.ChoiceField(
        choices=["local_cache", "youtube_api", "not_found"]
    )
    results = AlbumSerializer(many=True)
    message = serializers.CharField(required=False, help_text="Mensaje informativo")
