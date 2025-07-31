from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.music_catalog.infrastructure.repository import SongRepository
from apps.music_catalog.use_cases.song_use_cases import SongUseCases
from src.common.utils import get_logger

from ..serializers import (
    PlaySongRequestSerializer,
    SongDetailSerializer,
    SongSerializer,
)

logger = get_logger(__name__)

# Inicializar repositorio y casos de uso
song_repository = SongRepository()
song_use_cases = SongUseCases(song_repository)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_songs(request):
    """Obtener todas las canciones"""
    try:
        songs = song_use_cases.get_all_songs()
        serializer = SongSerializer(songs, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting all songs: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener las canciones"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_song_detail(request, song_id):
    """Obtener detalle de una canción"""
    try:
        song = song_use_cases.get_song_by_id(song_id)
        if not song:
            return Response(
                {"success": False, "error": "Canción no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SongDetailSerializer(song)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error getting song detail: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener la canción"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def play_song(request):
    """Reproducir una canción (incrementa contador)"""
    try:
        serializer = PlaySongRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        song_id = serializer.validated_data["song_id"]
        song = song_use_cases.play_song(song_id)

        if not song:
            return Response(
                {"success": False, "error": "Canción no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        song_serializer = SongDetailSerializer(song)
        return Response(
            {
                "success": True,
                "message": "Canción reproducida",
                "data": song_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error playing song: {str(e)}")
        return Response(
            {"success": False, "error": "Error al reproducir la canción"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_popular_songs(request):
    """Obtener canciones populares"""
    try:
        limit = int(request.GET.get("limit", 50))
        songs = song_use_cases.get_popular_songs(limit)
        serializer = SongSerializer(songs, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting popular songs: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener canciones populares"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_songs_by_artist(request, artist_id):
    """Obtener canciones de un artista"""
    try:
        songs = song_use_cases.get_songs_by_artist(artist_id)
        serializer = SongSerializer(songs, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting songs by artist: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener canciones del artista"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_songs_by_album(request, album_id):
    """Obtener canciones de un álbum"""
    try:
        songs = song_use_cases.get_songs_by_album(album_id)
        serializer = SongSerializer(songs, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting songs by album: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener canciones del álbum"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_songs_by_genre(request, genre_id):
    """Obtener canciones de un género"""
    try:
        songs = song_use_cases.get_songs_by_genre(genre_id)
        serializer = SongSerializer(songs, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting songs by genre: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener canciones del género"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
