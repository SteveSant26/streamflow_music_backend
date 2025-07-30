from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import Http404

from apps.music_catalog.use_cases.song_use_cases import SongUseCases
from apps.music_catalog.use_cases.artist_use_cases import ArtistUseCases
from apps.music_catalog.use_cases.album_use_cases import AlbumUseCases
from apps.music_catalog.use_cases.search_use_cases import SearchUseCases
from apps.music_catalog.infrastructure.repository import (
    SongRepository,
    ArtistRepository, 
    AlbumRepository,
    GenreRepository,
    MusicSearchRepository
)
from .serializers import (
    SongSerializer,
    SongDetailSerializer,
    ArtistSerializer,
    AlbumSerializer,
    GenreSerializer,
    SearchResultSerializer,
    PaginatedResultSerializer,
    PlaySongRequestSerializer,
    SearchRequestSerializer,
    FilterSearchRequestSerializer
)
from src.common.utils import get_logger

logger = get_logger(__name__)

# Inicializar repositorios
song_repository = SongRepository()
artist_repository = ArtistRepository()
album_repository = AlbumRepository()
genre_repository = GenreRepository()
search_repository = MusicSearchRepository()

# Inicializar casos de uso  
song_use_cases = SongUseCases(song_repository)
artist_use_cases = ArtistUseCases(artist_repository)
album_use_cases = AlbumUseCases(album_repository)
search_use_cases = SearchUseCases(search_repository)


# ========================
# ENDPOINTS DE CANCIONES
# ========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_songs(request):
    """Obtener todas las canciones"""
    try:
        songs = song_use_cases.get_all_songs()
        serializer = SongSerializer(songs, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting all songs: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener las canciones'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_song_detail(request, song_id):
    """Obtener detalle de una canción"""
    try:
        song = song_use_cases.get_song_by_id(song_id)
        if not song:
            return Response({
                'success': False,
                'error': 'Canción no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SongDetailSerializer(song)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting song detail: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener la canción'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def play_song(request):
    """Reproducir una canción (incrementa contador)"""
    try:
        serializer = PlaySongRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        song_id = serializer.validated_data['song_id']
        song = song_use_cases.play_song(song_id)
        
        if not song:
            return Response({
                'success': False,
                'error': 'Canción no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        song_serializer = SongDetailSerializer(song)
        return Response({
            'success': True,
            'message': 'Canción reproducida',
            'data': song_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error playing song: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al reproducir la canción'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_popular_songs(request):
    """Obtener canciones populares"""
    try:
        limit = int(request.GET.get('limit', 50))
        songs = song_use_cases.get_popular_songs(limit)
        serializer = SongSerializer(songs, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting popular songs: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener canciones populares'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_songs_by_artist(request, artist_id):
    """Obtener canciones de un artista"""
    try:
        songs = song_use_cases.get_songs_by_artist(artist_id)
        serializer = SongSerializer(songs, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting songs by artist: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener canciones del artista'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_songs_by_album(request, album_id):
    """Obtener canciones de un álbum"""
    try:
        songs = song_use_cases.get_songs_by_album(album_id)
        serializer = SongSerializer(songs, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting songs by album: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener canciones del álbum'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_songs_by_genre(request, genre_id):
    """Obtener canciones de un género"""
    try:
        songs = song_use_cases.get_songs_by_genre(genre_id)
        serializer = SongSerializer(songs, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting songs by genre: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener canciones del género'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========================
# ENDPOINTS DE ARTISTAS
# ========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_artists(request):
    """Obtener todos los artistas"""
    try:
        artists = artist_use_cases.get_all_artists()
        serializer = ArtistSerializer(artists, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting all artists: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener los artistas'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_artist_detail(request, artist_id):
    """Obtener detalle de un artista"""
    try:
        artist = artist_use_cases.get_artist_by_id(artist_id)
        if not artist:
            return Response({
                'success': False,
                'error': 'Artista no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ArtistSerializer(artist)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting artist detail: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener el artista'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_popular_artists(request):
    """Obtener artistas populares"""
    try:
        limit = int(request.GET.get('limit', 50))
        artists = artist_use_cases.get_popular_artists(limit)
        serializer = ArtistSerializer(artists, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting popular artists: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener artistas populares'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========================
# ENDPOINTS DE ÁLBUMES
# ========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_albums(request):
    """Obtener todos los álbumes"""
    try:
        albums = album_use_cases.get_all_albums()
        serializer = AlbumSerializer(albums, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting all albums: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener los álbumes'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_album_detail(request, album_id):
    """Obtener detalle de un álbum"""
    try:
        album = album_use_cases.get_album_by_id(album_id)
        if not album:
            return Response({
                'success': False,  
                'error': 'Álbum no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AlbumSerializer(album)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting album detail: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener el álbum'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_albums_by_artist(request, artist_id):
    """Obtener álbumes de un artista"""
    try:
        albums = album_use_cases.get_albums_by_artist(artist_id)
        serializer = AlbumSerializer(albums, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting albums by artist: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener álbumes del artista'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_popular_albums(request):
    """Obtener álbumes populares"""
    try:
        limit = int(request.GET.get('limit', 50))
        albums = album_use_cases.get_popular_albums(limit)
        serializer = AlbumSerializer(albums, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting popular albums: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener álbumes populares'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========================
# ENDPOINTS DE GÉNEROS
# ========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_genres(request):
    """Obtener todos los géneros"""
    try:
        genres = genre_repository.get_all()
        serializer = GenreSerializer(genres, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting all genres: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener los géneros'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_genre_detail(request, genre_id):
    """Obtener detalle de un género"""
    try:
        genre = genre_repository.get_by_id(genre_id)
        if not genre:
            return Response({
                'success': False,
                'error': 'Género no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GenreSerializer(genre)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting genre detail: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al obtener el género'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========================
# ENDPOINTS DE BÚSQUEDA
# ========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_all(request):
    """Búsqueda general en todas las categorías"""
    try:
        serializer = SearchRequestSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query']
        page = serializer.validated_data['page']
        page_size = serializer.validated_data['page_size']
        
        results = search_use_cases.search_all(query, page, page_size)
        result_serializer = SearchResultSerializer(results)
        
        return Response({
            'success': True,
            'data': result_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in search_all: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al realizar la búsqueda'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_songs(request):
    """Búsqueda paginada de canciones"""
    try:
        serializer = SearchRequestSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        query = serializer.validated_data['query']
        page = serializer.validated_data['page']
        page_size = serializer.validated_data['page_size']
        
        results = search_use_cases.search_songs_paginated(query, page, page_size)
        result_serializer = PaginatedResultSerializer(results)
        
        return Response({
            'success': True,
            'data': result_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in search_songs: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al buscar canciones'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_with_filters(request):
    """Búsqueda con filtros específicos"""
    try:
        serializer = FilterSearchRequestSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        filters = {k: v for k, v in serializer.validated_data.items() 
                  if k not in ['page', 'page_size'] and v is not None}
        page = serializer.validated_data['page']
        page_size = serializer.validated_data['page_size']
        
        results = search_use_cases.search_by_filters(filters, page, page_size)
        result_serializer = PaginatedResultSerializer(results)
        
        return Response({
            'success': True,
            'data': result_serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in search_with_filters: {str(e)}")
        return Response({
            'success': False,
            'error': 'Error al buscar con filtros'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
