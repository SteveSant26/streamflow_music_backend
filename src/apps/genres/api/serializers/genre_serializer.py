from rest_framework import serializers

from apps.genres.domain.entities import GenreEntity
from apps.genres.infrastructure.models.genre_model import GenreModel


class GenreSerializer(serializers.ModelSerializer):
    """Serializer para géneros musicales (solo lectura)"""

    class Meta:
        model = GenreModel
        fields = [
            "id",
            "name",
            "description",
            "image_url",
            "color_hex",
            "popularity_score",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["__all__"]  # Todos los campos son de solo lectura

    def to_representation(self, instance):
        """Convierte el modelo a representación JSON"""
        if isinstance(instance, GenreEntity):
            # Si recibimos una entidad, convertirla directamente
            return {
                "id": str(instance.id),
                "name": instance.name,
                "description": instance.description,
                "image_url": instance.image_url,
                "color_hex": instance.color_hex,
                "popularity_score": instance.popularity_score,
                "is_active": instance.is_active,
                "created_at": instance.created_at.isoformat()
                if instance.created_at
                else None,
                "updated_at": instance.updated_at.isoformat()
                if instance.updated_at
                else None,
            }
        return super().to_representation(instance)


class GenreSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de géneros"""

    q = serializers.CharField(max_length=100, help_text="Texto de búsqueda")


class GenreSearchResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de búsqueda de géneros"""

    query = serializers.CharField()
    results = GenreSerializer(many=True)
    total = serializers.IntegerField()
