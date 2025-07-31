from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.music_catalog.infrastructure.repository import GenreRepository
from src.common.utils import get_logger

from ..serializers import GenreSerializer

logger = get_logger(__name__)

# Inicializar repositorio
genre_repository = GenreRepository()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_genres(request):
    """Obtener todos los géneros"""
    try:
        genres = genre_repository.get_all()
        serializer = GenreSerializer(genres, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting all genres: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener los géneros"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_genre_detail(request, genre_id):
    """Obtener detalle de un género"""
    try:
        genre = genre_repository.get_by_id(genre_id)
        if not genre:
            return Response(
                {"success": False, "error": "Género no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = GenreSerializer(genre)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error getting genre detail: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener el género"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
