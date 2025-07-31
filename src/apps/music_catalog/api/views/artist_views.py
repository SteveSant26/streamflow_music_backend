from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.music_catalog.infrastructure.repository import ArtistRepository
from apps.music_catalog.use_cases.artist_use_cases import ArtistUseCases
from src.common.utils import get_logger

from ..serializers import ArtistDetailSerializer, ArtistSerializer

logger = get_logger(__name__)

# Inicializar repositorio y casos de uso
artist_repository = ArtistRepository()
artist_use_cases = ArtistUseCases(artist_repository)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_artists(request):
    """Obtener todos los artistas"""
    try:
        artists = artist_use_cases.get_all_artists()
        serializer = ArtistSerializer(artists, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting all artists: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener los artistas"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_artist_detail(request, artist_id):
    """Obtener detalle de un artista"""
    try:
        artist = artist_use_cases.get_artist_by_id(artist_id)
        if not artist:
            return Response(
                {"success": False, "error": "Artista no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ArtistDetailSerializer(artist)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error getting artist detail: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener el artista"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_popular_artists(request):
    """Obtener artistas populares"""
    try:
        limit = int(request.GET.get("limit", 50))
        artists = artist_use_cases.get_popular_artists(limit)
        serializer = ArtistSerializer(artists, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting popular artists: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener artistas populares"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_artists_by_genre(request, genre_id):
    """Obtener artistas por género"""
    try:
        artists = artist_use_cases.get_artists_by_genre(genre_id)
        serializer = ArtistSerializer(artists, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting artists by genre: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener artistas del género"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
