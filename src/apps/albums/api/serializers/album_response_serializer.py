from rest_framework import serializers

<<<<<<< HEAD
from apps.albums.api.dtos import AlbumResponseDTO
from apps.albums.api.mappers import AlbumMapper
from apps.albums.domain.entities import AlbumEntity
from common.serializers import BaseEntitySerializer


class AlbumResponseSerializer(BaseEntitySerializer):
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
    artist_name = serializers.CharField(read_only=True, required=False, allow_null=True)
    release_date = serializers.DateField(
        read_only=True, required=False, allow_null=True
    )
    description = serializers.CharField(read_only=True, required=False, allow_null=True)
    cover_image_url = serializers.URLField(
        read_only=True, required=False, allow_null=True
    )
    total_tracks = serializers.IntegerField(read_only=True)
    play_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(
        read_only=True, required=False, allow_null=True
    )
    updated_at = serializers.DateTimeField(
        read_only=True, required=False, allow_null=True
    )


class AlbumSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de álbumes"""

    q = serializers.CharField(max_length=255, help_text="Texto de búsqueda")
    artist_id = serializers.UUIDField(
        required=False, help_text="ID del artista (opcional)"
    )
    artist_name = serializers.CharField(
        max_length=200, required=False, help_text="Nombre del artista (opcional)"
    )
    limit = serializers.IntegerField(
        default=10, min_value=1, max_value=50, help_text="Límite de resultados"
=======
from apps.albums.infrastructure.models.album_model import AlbumModel


class AlbumResponseSerializer(serializers.ModelSerializer):
    """Serializer para respuestas de álbumes que trabaja directamente con el modelo"""

    # Campos calculados para incluir información del artista
    artist_name = serializers.CharField(source="artist.name", read_only=True)
    artist_verified = serializers.BooleanField(
        source="artist.is_verified", read_only=True
    )

    class Meta:
        model = AlbumModel
        fields = [
            "id",
            "title",
            "artist_id",
            "artist_name",
            "artist_verified",
            "release_date",
            "description",
            "cover_image_url",
            "total_tracks",
            "play_count",
            "source_type",
            "source_id",
            "source_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            fields  # Todos los campos son de solo lectura para respuestas
        )


class CreateAlbumSerializer(serializers.ModelSerializer):
    """Serializer para crear álbumes"""

    class Meta:
        model = AlbumModel
        fields = [
            "title",
            "artist_id",
            "release_date",
            "description",
            "cover_image_url",
            "total_tracks",
            "source_type",
            "source_id",
            "source_url",
        ]

    def validate_title(self, value):
        """Validar que el título no esté vacío"""
        if not value.strip():
            raise serializers.ValidationError(
                "El título del álbum no puede estar vacío"
            )
        return value

    def validate_total_tracks(self, value):
        """Validar que el número de pistas sea positivo"""
        if value < 0:
            raise serializers.ValidationError(
                "El número de pistas no puede ser negativo"
            )
        return value


class UpdateAlbumSerializer(serializers.ModelSerializer):
    """Serializer para actualizar álbumes"""

    class Meta:
        model = AlbumModel
        fields = [
            "title",
            "release_date",
            "description",
            "cover_image_url",
            "total_tracks",
            "play_count",
        ]

    def validate_title(self, value):
        """Validar que el título no esté vacío"""
        if value and not value.strip():
            raise serializers.ValidationError(
                "El título del álbum no puede estar vacío"
            )
        return value

    def validate_total_tracks(self, value):
        """Validar que el número de pistas sea positivo"""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "El número de pistas no puede ser negativo"
            )
        return value


class AlbumSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de álbumes (mantener para compatibilidad si es necesario)"""

    search = serializers.CharField(
        max_length=255, help_text="Texto de búsqueda general"
    )
    title = serializers.CharField(
        max_length=300, required=False, help_text="Búsqueda por título"
    )
    artist_name = serializers.CharField(
        max_length=200, required=False, help_text="Búsqueda por nombre del artista"
    )
    release_year = serializers.IntegerField(
        required=False, help_text="Año de lanzamiento"
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
    )


class AlbumSearchResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de búsqueda de álbumes"""

    source = serializers.ChoiceField(
        choices=["local_cache", "youtube_api", "not_found"]
    )
    results = AlbumResponseSerializer(many=True)
    message = serializers.CharField(required=False, help_text="Mensaje informativo")
