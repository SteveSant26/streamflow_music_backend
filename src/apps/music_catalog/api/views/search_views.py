from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.music_catalog.infrastructure.repository import MusicSearchRepository
from apps.music_catalog.use_cases.search_use_cases import SearchUseCases
from src.common.utils import get_logger

from ..serializers import (
    FilterSearchRequestSerializer,
    PaginatedResultSerializer,
    SearchRequestSerializer,
    SearchResultSerializer,
)

logger = get_logger(__name__)

# Inicializar repositorio y casos de uso
search_repository = MusicSearchRepository()
search_use_cases = SearchUseCases(search_repository)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def search_all(request):
    """Búsqueda general en todas las entidades"""
    try:
        serializer = SearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = serializer.validated_data["query"]
        page = serializer.validated_data["page"]
        page_size = serializer.validated_data["page_size"]

        # Búsqueda general simplificada
        results = search_use_cases.search_all(query, page, page_size)
        result_serializer = SearchResultSerializer(results)

        return Response(
            {"success": True, "data": result_serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error in search all: {str(e)}")
        return Response(
            {"success": False, "error": "Error en la búsqueda"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def search_songs(request):
    """Búsqueda específica de canciones"""
    try:
        serializer = SearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = serializer.validated_data["query"]
        page = serializer.validated_data["page"]
        page_size = serializer.validated_data["page_size"]

        results = search_use_cases.search_songs(query, page, page_size)
        result_serializer = PaginatedResultSerializer(results)

        return Response(
            {"success": True, "data": result_serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error in search songs: {str(e)}")
        return Response(
            {"success": False, "error": "Error en la búsqueda de canciones"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def search_artists(request):
    """Búsqueda específica de artistas"""
    try:
        serializer = SearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = serializer.validated_data["query"]
        page = serializer.validated_data["page"]
        page_size = serializer.validated_data["page_size"]

        results = search_use_cases.search_artists(query, page, page_size)
        result_serializer = PaginatedResultSerializer(results)

        return Response(
            {"success": True, "data": result_serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error in search artists: {str(e)}")
        return Response(
            {"success": False, "error": "Error en la búsqueda de artistas"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def search_albums(request):
    """Búsqueda específica de álbumes"""
    try:
        serializer = SearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = serializer.validated_data["query"]
        page = serializer.validated_data["page"]
        page_size = serializer.validated_data["page_size"]

        results = search_use_cases.search_albums(query, page, page_size)
        result_serializer = PaginatedResultSerializer(results)

        return Response(
            {"success": True, "data": result_serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error in search albums: {str(e)}")
        return Response(
            {"success": False, "error": "Error en la búsqueda de álbumes"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def advanced_search(request):
    """Búsqueda avanzada con filtros"""
    try:
        serializer = FilterSearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extraer filtros y parámetros de paginación
        filters = {
            k: v
            for k, v in serializer.validated_data.items()
            if k not in ["page", "page_size"] and v is not None
        }
        page = serializer.validated_data["page"]
        page_size = serializer.validated_data["page_size"]

        results = search_use_cases.advanced_search(filters, page, page_size)
        result_serializer = PaginatedResultSerializer(results)

        return Response(
            {"success": True, "data": result_serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error in advanced search: {str(e)}")
        return Response(
            {"success": False, "error": "Error en la búsqueda avanzada"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
