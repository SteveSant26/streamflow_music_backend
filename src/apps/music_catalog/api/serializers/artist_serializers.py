from rest_framework import serializers


class ArtistSerializer(serializers.Serializer):
    """Serializer base para entidad de artista"""

    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=200)
    biography = serializers.CharField(required=False, allow_blank=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    followers_count = serializers.IntegerField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ArtistListSerializer(ArtistSerializer):
    """Serializer para lista de artistas (campos resumidos)"""

    class Meta:
        fields = ["id", "name", "image_url", "followers_count", "is_verified"]


class ArtistDetailSerializer(ArtistSerializer):
    """Serializer detallado para artista con información completa"""
