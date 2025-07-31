from rest_framework import serializers


class SongSerializer(serializers.Serializer):
    """Serializer base para entidad de canción"""

    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=200)
    artist_id = serializers.CharField()
    artist_name = serializers.CharField(read_only=True)
    album_id = serializers.CharField(required=False, allow_null=True)
    album_title = serializers.CharField(read_only=True, required=False)
    duration_seconds = serializers.IntegerField()
    file_url = serializers.URLField()
    lyrics = serializers.CharField(required=False, allow_blank=True)
    track_number = serializers.IntegerField(required=False)
    genre_id = serializers.CharField(required=False, allow_null=True)
    genre_name = serializers.CharField(read_only=True, required=False)
    play_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class SongListSerializer(SongSerializer):
    """Serializer para lista de canciones (campos resumidos)"""

    class Meta:
        fields = [
            "id",
            "title",
            "artist_name",
            "album_title",
            "duration_seconds",
            "play_count",
            "genre_name",
        ]


class SongDetailSerializer(SongSerializer):
    """Serializer detallado para canción con información completa"""
