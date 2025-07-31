from rest_framework import serializers

from apps.albums.domain.entities import AlbumEntity
from apps.albums.infrastructure.models.album_model import AlbumModel


class AlbumSerializer(serializers.ModelSerializer):
    """Serializer para álbumes (solo lectura - datos de YouTube)"""

    class Meta:
        model = AlbumModel
        fields = [
            "id",
            "title",
            "artist_id",
            "artist_name",
            "release_date",
            "description",
            "cover_image_url",
            "total_tracks",
            "play_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["__all__"]  # Todos los campos son de solo lectura

    def to_representation(self, instance):
        """Convierte el modelo a representación JSON"""
        if isinstance(instance, AlbumEntity):
            # Si recibimos una entidad, convertirla directamente
            return {
                "id": str(instance.id),
                "title": instance.title,
                "artist_id": str(instance.artist_id),
                "artist_name": instance.artist_name,
                "release_date": instance.release_date.isoformat()
                if instance.release_date
                else None,
                "description": instance.description,
                "cover_image_url": instance.cover_image_url,
                "total_tracks": instance.total_tracks,
                "play_count": instance.play_count,
                "is_active": instance.is_active,
                "created_at": instance.created_at.isoformat()
                if instance.created_at
                else None,
                "updated_at": instance.updated_at.isoformat()
                if instance.updated_at
                else None,
            }
        return super().to_representation(instance)


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
