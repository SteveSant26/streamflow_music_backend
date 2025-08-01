from rest_framework import serializers

from common.serializers.base_entity_serializer import BaseEntitySerializer

from ..dtos import GenreResponseDTO


class GenreSerializer(BaseEntitySerializer[GenreResponseDTO]):
    """Serializer para géneros musicales (solo lectura)"""

    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True, allow_null=True)
    image_url = serializers.URLField(read_only=True, allow_null=True)
    color_hex = serializers.CharField(read_only=True, allow_null=True)
    popularity_score = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        dto_class = GenreResponseDTO


class GenreSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de géneros"""

    q = serializers.CharField(max_length=100, help_text="Texto de búsqueda")


class GenreSearchResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de búsqueda de géneros"""

    query = serializers.CharField()
    results = GenreSerializer(many=True)
    total = serializers.IntegerField()
