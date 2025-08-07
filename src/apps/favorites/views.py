from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import FavoriteSongModel, FavoriteArtistModel, FavoriteAlbumModel
from .serializers import (
    FavoriteSongSerializer, 
    FavoriteArtistSerializer, 
    FavoriteAlbumSerializer,
    AddToFavoritesDto
)
from apps.songs.infrastructure.models import SongModel
from apps.artists.infrastructure.models import ArtistModel
from apps.albums.infrastructure.models import AlbumModel


@extend_schema_view(
    list=extend_schema(
        tags=["Favorites"],
        description="Get user's favorite songs",
        summary="Get favorite songs"
    ),
    create=extend_schema(
        tags=["Favorites"],
        description="Add a song to favorites",
        summary="Add song to favorites"
    ),
    destroy=extend_schema(
        tags=["Favorites"],
        description="Remove a song from favorites",
        summary="Remove song from favorites"
    )
)
class FavoriteSongViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSongSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'song_id'
    
    def get_queryset(self):
        return FavoriteSongModel.objects.filter(user=self.request.user).select_related('song', 'song__artist')
    
    def create(self, request, *args, **kwargs):
        """Agregar canción a favoritos"""
        song_id = request.data.get('song_id')
        if not song_id:
            return Response(
                {'error': 'song_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            song = SongModel.objects.get(id=song_id)
        except SongModel.DoesNotExist:
            return Response(
                {'error': 'Song not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            favorite, created = FavoriteSongModel.objects.get_or_create(
                user=request.user,
                song=song
            )
            
            if created:
                # Incrementar contador de favoritos en la canción
                song.favorite_count += 1
                song.save(update_fields=['favorite_count'])
                
                serializer = self.get_serializer(favorite)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'message': 'Song already in favorites'}, 
                    status=status.HTTP_200_OK
                )
                
        except IntegrityError:
            return Response(
                {'error': 'Song already in favorites'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Remover canción de favoritos"""
        song_id = kwargs.get('song_id')
        
        try:
            favorite = FavoriteSongModel.objects.get(
                user=request.user,
                song_id=song_id
            )
            
            # Decrementar contador de favoritos en la canción
            song = favorite.song
            if song.favorite_count > 0:
                song.favorite_count -= 1
                song.save(update_fields=['favorite_count'])
            
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except FavoriteSongModel.DoesNotExist:
            return Response(
                {'error': 'Song not found in favorites'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        tags=["Favorites"],
        description="Check if a song is in favorites",
        summary="Check if song is favorite"
    )
    @action(detail=True, methods=['get'], url_path='check')
    def check_favorite(self, request, song_id=None):
        """Verificar si una canción está en favoritos"""
        is_favorite = FavoriteSongModel.objects.filter(
            user=request.user,
            song_id=song_id
        ).exists()
        
        return Response({
            'is_favorite': is_favorite,
            'song_id': song_id
        })


@extend_schema_view(
    list=extend_schema(
        tags=["Favorites"],
        description="Get user's favorite artists",
        summary="Get favorite artists"
    ),
    create=extend_schema(
        tags=["Favorites"],
        description="Add an artist to favorites",
        summary="Add artist to favorites"
    ),
    destroy=extend_schema(
        tags=["Favorites"],
        description="Remove an artist from favorites",
        summary="Remove artist from favorites"
    )
)
class FavoriteArtistViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteArtistSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'artist_id'
    
    def get_queryset(self):
        return FavoriteArtistModel.objects.filter(user=self.request.user).select_related('artist')
    
    def create(self, request, *args, **kwargs):
        """Agregar artista a favoritos"""
        artist_id = request.data.get('artist_id')
        if not artist_id:
            return Response(
                {'error': 'artist_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            artist = ArtistModel.objects.get(id=artist_id)
        except ArtistModel.DoesNotExist:
            return Response(
                {'error': 'Artist not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            favorite, created = FavoriteArtistModel.objects.get_or_create(
                user=request.user,
                artist=artist
            )
            
            if created:
                # Incrementar contador de seguidores del artista
                artist.followers_count += 1
                artist.save(update_fields=['followers_count'])
                
                serializer = self.get_serializer(favorite)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'message': 'Artist already in favorites'}, 
                    status=status.HTTP_200_OK
                )
                
        except IntegrityError:
            return Response(
                {'error': 'Artist already in favorites'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Remover artista de favoritos"""
        artist_id = kwargs.get('artist_id')
        
        try:
            favorite = FavoriteArtistModel.objects.get(
                user=request.user,
                artist_id=artist_id
            )
            
            # Decrementar contador de seguidores del artista
            artist = favorite.artist
            if artist.followers_count > 0:
                artist.followers_count -= 1
                artist.save(update_fields=['followers_count'])
            
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except FavoriteArtistModel.DoesNotExist:
            return Response(
                {'error': 'Artist not found in favorites'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    list=extend_schema(
        tags=["Favorites"],
        description="Get user's favorite albums",
        summary="Get favorite albums"
    ),
    create=extend_schema(
        tags=["Favorites"],
        description="Add an album to favorites",
        summary="Add album to favorites"
    ),
    destroy=extend_schema(
        tags=["Favorites"],
        description="Remove an album from favorites",
        summary="Remove album from favorites"
    )
)
class FavoriteAlbumViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteAlbumSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'album_id'
    
    def get_queryset(self):
        return FavoriteAlbumModel.objects.filter(user=self.request.user).select_related('album', 'album__artist')
    
    def create(self, request, *args, **kwargs):
        """Agregar álbum a favoritos"""
        album_id = request.data.get('album_id')
        if not album_id:
            return Response(
                {'error': 'album_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            album = AlbumModel.objects.get(id=album_id)
        except AlbumModel.DoesNotExist:
            return Response(
                {'error': 'Album not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            favorite, created = FavoriteAlbumModel.objects.get_or_create(
                user=request.user,
                album=album
            )
            
            if created:
                serializer = self.get_serializer(favorite)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'message': 'Album already in favorites'}, 
                    status=status.HTTP_200_OK
                )
                
        except IntegrityError:
            return Response(
                {'error': 'Album already in favorites'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Remover álbum de favoritos"""
        album_id = kwargs.get('album_id')
        
        try:
            favorite = FavoriteAlbumModel.objects.get(
                user=request.user,
                album_id=album_id
            )
            
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except FavoriteAlbumModel.DoesNotExist:
            return Response(
                {'error': 'Album not found in favorites'}, 
                status=status.HTTP_404_NOT_FOUND
            )
