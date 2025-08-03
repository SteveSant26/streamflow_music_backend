from rest_framework import serializers

from apps.genres.api.mappers import GenreMapper
from apps.genres.domain.entities import GenreEntity
from common.serializers import BaseEntitySerializer

from ..dtos import GenreResponseDTO


class GenreSerializer(BaseEntitySerializer):
    """
    Serializer inteligente que hereda funcionalidad automática de conversión.
    Solo necesita definir las clases correspondientes.
    """

    # Configuración para el serializer base
    mapper_class = GenreMapper()
    entity_class = GenreEntity
    dto_class = GenreResponseDTO

    # Definición de campos (opcional, solo para documentación/validación)
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    image_url = serializers.URLField(read_only=True, allow_null=True)
    color_hex = serializers.CharField(read_only=True, allow_null=True)
    popularity_score = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)


class GenreSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de géneros"""

    q = serializers.CharField(max_length=100, help_text="Texto de búsqueda")


class GenreSearchResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de búsqueda de géneros"""

    query = serializers.CharField()
    results = GenreSerializer(many=True)
    total = serializers.IntegerField()
