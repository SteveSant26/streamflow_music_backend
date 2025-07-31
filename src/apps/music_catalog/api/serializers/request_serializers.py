from rest_framework import serializers


class PlaySongRequestSerializer(serializers.Serializer):
    """Serializer para request de reproducir canción"""

    song_id = serializers.CharField()


class SearchRequestSerializer(serializers.Serializer):
    """Serializer para request de búsqueda"""

    query = serializers.CharField(max_length=200)
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)


class FilterSearchRequestSerializer(serializers.Serializer):
    """Serializer para búsqueda con filtros"""

    genre_id = serializers.CharField(required=False, allow_blank=True)
    artist_id = serializers.CharField(required=False, allow_blank=True)
    album_id = serializers.CharField(required=False, allow_blank=True)
    year = serializers.IntegerField(required=False, min_value=1900, max_value=2100)
    duration_min = serializers.IntegerField(required=False, min_value=0)  # en minutos
    duration_max = serializers.IntegerField(required=False, min_value=0)  # en minutos
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)
