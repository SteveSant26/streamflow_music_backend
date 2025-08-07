from rest_framework import serializers
from .models import FavoriteSongModel, FavoriteArtistModel, FavoriteAlbumModel


class FavoriteSongSerializer(serializers.ModelSerializer):
    song_title = serializers.CharField(source='song.title', read_only=True)
    song_artist = serializers.CharField(source='song.artist.name', read_only=True)
    song_thumbnail = serializers.URLField(source='song.thumbnail_url', read_only=True)
    song_duration = serializers.IntegerField(source='song.duration_seconds', read_only=True)
    
    class Meta:
        model = FavoriteSongModel
        fields = [
            'id', 'song', 'song_title', 'song_artist', 'song_thumbnail', 
            'song_duration', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FavoriteArtistSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.name', read_only=True)
    artist_image = serializers.URLField(source='artist.image_url', read_only=True)
    artist_followers = serializers.IntegerField(source='artist.followers_count', read_only=True)
    
    class Meta:
        model = FavoriteArtistModel
        fields = [
            'id', 'artist', 'artist_name', 'artist_image', 
            'artist_followers', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FavoriteAlbumSerializer(serializers.ModelSerializer):
    album_title = serializers.CharField(source='album.title', read_only=True)
    album_artist = serializers.CharField(source='album.artist.name', read_only=True)
    album_cover = serializers.URLField(source='album.cover_url', read_only=True)
    album_year = serializers.IntegerField(source='album.release_year', read_only=True)
    
    class Meta:
        model = FavoriteAlbumModel
        fields = [
            'id', 'album', 'album_title', 'album_artist', 
            'album_cover', 'album_year', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# DTOs para requests
class AddToFavoritesDto(serializers.Serializer):
    """DTO para agregar elementos a favoritos"""
    pass  # Solo necesitamos el ID del elemento que viene en la URL


class RemoveFromFavoritesDto(serializers.Serializer):
    """DTO para remover elementos de favoritos"""
    pass  # Solo necesitamos el ID del elemento que viene en la URL
