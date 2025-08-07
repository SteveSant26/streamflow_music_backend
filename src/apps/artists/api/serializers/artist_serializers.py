from rest_framework import serializers

from apps.artists.infrastructure.models.artist_model import ArtistModel


class ArtistResponseSerializer(serializers.ModelSerializer):
    """Serializer para respuestas de artistas que trabaja directamente con el modelo"""

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
