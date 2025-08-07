from rest_framework import serializers

from apps.artists.infrastructure.models.artist_model import ArtistModel


class ArtistResponseSerializer(serializers.ModelSerializer):
    """Serializer para respuestas de artistas que trabaja directamente con el modelo"""

<<<<<<< HEAD
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
=======
    class Meta:
        model = ArtistModel
        fields = [
            "id",
            "name",
            "biography",
            "image_url",
            "followers_count",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            fields  # Todos los campos son de solo lectura para respuestas
        )
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33


class CreateArtistSerializer(serializers.ModelSerializer):
    """Serializer para crear artistas"""

    class Meta:
        model = ArtistModel
        fields = [
            "name",
            "biography",
            "image_url",
        ]

    def validate_name(self, value):
        """Validar que el nombre no esté vacío"""
        if not value.strip():
            raise serializers.ValidationError(
                "El nombre del artista no puede estar vacío"
            )
        return value


class UpdateArtistSerializer(serializers.ModelSerializer):
    """Serializer para actualizar artistas"""

    class Meta:
        model = ArtistModel
        fields = [
            "name",
            "biography",
            "image_url",
            "followers_count",
            "is_verified",
        ]

    def validate_name(self, value):
        """Validar que el nombre no esté vacío"""
        if value and not value.strip():
            raise serializers.ValidationError(
                "El nombre del artista no puede estar vacío"
            )
        return value
