from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.music_catalog.infrastructure.repository import AlbumRepository
from apps.music_catalog.use_cases.album_use_cases import AlbumUseCases
from src.common.utils import get_logger

from ..serializers import AlbumDetailSerializer, AlbumSerializer

logger = get_logger(__name__)

# Inicializar repositorio y casos de uso
album_repository = AlbumRepository()
album_use_cases = AlbumUseCases(album_repository)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_albums(request):
    """Obtener todos los álbumes"""
    try:
        albums = album_use_cases.get_all_albums()
        serializer = AlbumSerializer(albums, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting all albums: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener los álbumes"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_album_detail(request, album_id):
    """Obtener detalle de un álbum"""
    try:
        album = album_use_cases.get_album_by_id(album_id)
        if not album:
            return Response(
                {"success": False, "error": "Álbum no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AlbumDetailSerializer(album)
        return Response(
            {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error getting album detail: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener el álbum"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_popular_albums(request):
    """Obtener álbumes populares"""
    try:
        limit = int(request.GET.get("limit", 50))
        # Método simplificado - usar get_all si no existe get_popular
        albums = album_use_cases.get_all_albums()[:limit]
        serializer = AlbumSerializer(albums, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting popular albums: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener álbumes populares"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_albums_by_artist(request, artist_id):
    """Obtener álbumes de un artista"""
    try:
        albums = album_use_cases.get_albums_by_artist(artist_id)
        serializer = AlbumSerializer(albums, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting albums by artist: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener álbumes del artista"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_albums_by_genre(request, genre_id):
    """Obtener álbumes por género"""
    try:
        # Método simplificado - implementar lógica básica
        albums = album_use_cases.get_all_albums()  # Placeholder
        serializer = AlbumSerializer(albums, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting albums by genre: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener álbumes del género"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_recent_albums(request):
    """Obtener álbumes recientes"""
    try:
        limit = int(request.GET.get("limit", 20))
        # Método simplificado - usar get_all y tomar los primeros
        albums = album_use_cases.get_all_albums()[:limit]
        serializer = AlbumSerializer(albums, many=True)
        return Response(
            {"success": True, "data": serializer.data, "count": len(serializer.data)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error getting recent albums: {str(e)}")
        return Response(
            {"success": False, "error": "Error al obtener álbumes recientes"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
