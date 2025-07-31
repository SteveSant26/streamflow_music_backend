from rest_framework import serializers


class AlbumSerializer(serializers.Serializer):
    """Serializer base para entidad de álbum"""

    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=200)
    artist_id = serializers.CharField()
    artist_name = serializers.CharField(read_only=True)
    release_date = serializers.DateField()
    description = serializers.CharField(required=False, allow_blank=True)
    cover_image_url = serializers.URLField(required=False, allow_blank=True)
    total_tracks = serializers.IntegerField(read_only=True)
    play_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class AlbumListSerializer(AlbumSerializer):
    """Serializer para lista de álbumes (campos resumidos)"""

    class Meta:
        fields = [
            "id",
            "title",
            "artist_name",
            "cover_image_url",
            "release_date",
            "total_tracks",
        ]


class AlbumDetailSerializer(AlbumSerializer):
    """Serializer detallado para álbum con información completa"""
