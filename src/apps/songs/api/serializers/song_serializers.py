from rest_framework import serializers


class SongSerializer(serializers.Serializer):
    """Serializer para canciones"""

    id = serializers.UUIDField(read_only=True)
    title = serializers.CharField(max_length=255)
    youtube_video_id = serializers.CharField(max_length=20)
    artist_name = serializers.CharField(max_length=255, allow_null=True)
    album_title = serializers.CharField(max_length=255, allow_null=True)
    genre_name = serializers.CharField(max_length=100, allow_null=True)
    duration_seconds = serializers.IntegerField(min_value=0)
    duration_formatted = serializers.SerializerMethodField()
    file_url = serializers.URLField(allow_null=True)
    thumbnail_url = serializers.URLField(allow_null=True)
    youtube_url = serializers.URLField()
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50), allow_empty=True, required=False
    )
    play_count = serializers.IntegerField(min_value=0)
    youtube_view_count = serializers.IntegerField(min_value=0)
    youtube_like_count = serializers.IntegerField(min_value=0)
    is_explicit = serializers.BooleanField()
    audio_downloaded = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    published_at = serializers.DateTimeField(allow_null=True)

    def get_duration_formatted(self, obj) -> str:
        """Retorna la duración en formato MM:SS"""
        duration = (
            obj.get("duration_seconds", 0)
            if isinstance(obj, dict)
            else obj.duration_seconds
        )
        minutes = duration // 60
        seconds = duration % 60
        return f"{minutes:02d}:{seconds:02d}"


class SongListSerializer(serializers.Serializer):
    """Serializer simplificado para listas de canciones"""

    id = serializers.UUIDField()
    title = serializers.CharField()
    artist_name = serializers.CharField(allow_null=True)
    album_title = serializers.CharField(allow_null=True)
    duration_formatted = serializers.SerializerMethodField()
    thumbnail_url = serializers.URLField(allow_null=True)
    play_count = serializers.IntegerField()
    audio_downloaded = serializers.BooleanField()

    def get_duration_formatted(self, obj) -> str:
        """Retorna la duración en formato MM:SS"""
        duration = (
            obj.get("duration_seconds", 0)
            if isinstance(obj, dict)
            else obj.duration_seconds
        )
        minutes = duration // 60
        seconds = duration % 60
        return f"{minutes:02d}:{seconds:02d}"


class SearchRequestSerializer(serializers.Serializer):
    """Serializer para requests de búsqueda"""

    query = serializers.CharField(max_length=255, required=True)
    limit = serializers.IntegerField(min_value=1, max_value=50, default=20)
    include_youtube = serializers.BooleanField(default=True)


class RandomSongsRequestSerializer(serializers.Serializer):
    """Serializer para requests de canciones aleatorias"""

    count = serializers.IntegerField(min_value=1, max_value=20, default=6)
    force_refresh = serializers.BooleanField(default=False)


class ProcessVideoRequestSerializer(serializers.Serializer):
    """Serializer para procesar un video específico de YouTube"""

    video_id = serializers.CharField(max_length=20, required=True)

    def validate_video_id(self, value):
        """Valida el formato del video ID"""
        import re

        if not re.match(r"^[a-zA-Z0-9_-]{11}$", value):
            raise serializers.ValidationError("Invalid YouTube video ID format")
        return value


class SongStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de canciones"""

    total_songs = serializers.IntegerField()
    total_artists = serializers.IntegerField()
    total_play_count = serializers.IntegerField()
    songs_with_audio = serializers.IntegerField()
    most_played_song = SongListSerializer(allow_null=True)
    recent_songs = SongListSerializer(many=True)
