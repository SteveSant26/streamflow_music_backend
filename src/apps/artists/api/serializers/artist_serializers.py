from rest_framework import serializers

from apps.artists.api.dtos import ArtistResponseDTO
from apps.artists.api.mappers import ArtistMapper
from apps.artists.domain.entities import ArtistEntity
from common.serializers import BaseEntitySerializer


class ArtistResponseSerializer(BaseEntitySerializer):
    """Serializer para respuestas de artistas"""

    # Configuración para el serializer base
    mapper_class = ArtistMapper()
    entity_class = ArtistEntity
    dto_class = ArtistResponseDTO

    # Definición de campos
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    biography = serializers.CharField(read_only=True, required=False, allow_null=True)
    country = serializers.CharField(read_only=True, required=False, allow_null=True)
    image_url = serializers.URLField(read_only=True, required=False, allow_null=True)
    followers_count = serializers.IntegerField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, required=False)
    updated_at = serializers.DateTimeField(read_only=True, required=False)


class CreateArtistSerializer(serializers.Serializer):
    """Serializer para crear artistas"""

    name = serializers.CharField(max_length=200)
    biography = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country = serializers.CharField(
        max_length=100, required=False, allow_blank=True, allow_null=True
    )
    image_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)


class UpdateArtistSerializer(serializers.Serializer):
    """Serializer para actualizar artistas"""

    name = serializers.CharField(max_length=200, required=False)
    biography = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country = serializers.CharField(
        max_length=100, required=False, allow_blank=True, allow_null=True
    )
    image_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    followers_count = serializers.IntegerField(min_value=0, required=False)
    is_verified = serializers.BooleanField(required=False)
