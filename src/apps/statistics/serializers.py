from rest_framework import serializers


class UserStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas del usuario"""
    songs_played = serializers.IntegerField(help_text="Total de canciones reproducidas")
    hours_listened = serializers.FloatField(help_text="Total de horas escuchadas")
    playlists_created = serializers.IntegerField(help_text="Total de playlists creadas")
    favorite_artists = serializers.IntegerField(help_text="Total de artistas favoritos")


class TopArtistSerializer(serializers.Serializer):
    """Serializer para artistas más escuchados"""
    id = serializers.UUIDField()
    name = serializers.CharField()
    total_plays = serializers.IntegerField()
    image_url = serializers.URLField(allow_null=True)


class TopSongSerializer(serializers.Serializer):
    """Serializer para canciones más reproducidas"""
    id = serializers.UUIDField()
    title = serializers.CharField()
    artist_name = serializers.CharField()
    play_count = serializers.IntegerField()
    duration_seconds = serializers.IntegerField()
    thumbnail_url = serializers.URLField(allow_null=True)


class UserTopContentSerializer(serializers.Serializer):
    """Serializer para contenido top del usuario"""
    top_artists = TopArtistSerializer(many=True)
    top_songs = TopSongSerializer(many=True)


class GlobalStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas globales"""
    total_songs = serializers.IntegerField()
    total_artists = serializers.IntegerField()
    total_albums = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_plays = serializers.IntegerField()
    most_popular_genre = serializers.CharField(allow_null=True)
