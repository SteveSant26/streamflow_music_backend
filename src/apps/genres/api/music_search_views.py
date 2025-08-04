from asgiref.sync import async_to_sync
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..infrastructure.repository.genre_repository import GenreRepository
from ..use_cases.search_music_by_genre_use_case import SearchMusicByGenreUseCase


@extend_schema(
    summary="Buscar música por género",
    description="Devuelve una lista de videos relacionados con el género musical dado",
    parameters=[
        OpenApiParameter(
            name="genre",
            type=OpenApiTypes.STR,
            required=True,
            location=OpenApiParameter.QUERY,
            description="Nombre del género",
        ),
        OpenApiParameter(
            name="max_results",
            type=OpenApiTypes.INT,
            required=False,
            location=OpenApiParameter.QUERY,
            description="Cantidad máxima de resultados (default: 20, máximo: 50)",
        ),
        OpenApiParameter(
            name="order",
            type=OpenApiTypes.STR,
            required=False,
            location=OpenApiParameter.QUERY,
            description="Criterio de orden: relevance, date, rating, viewCount, title",
        ),
    ],
    responses={200: OpenApiTypes.OBJECT},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def search_music_by_genre_api(request):
    """
    Busca música por género específico usando la API de YouTube.

    Query Parameters:
    - genre: str (required) - Nombre del género
    - max_results: int (default: 20) - Número máximo de resultados
    - order: str (default: relevance) - Orden de resultados
    """
    try:
        genre_name = request.GET.get("genre")
        if not genre_name:
            return Response(
                {"success": False, "error": 'Parámetro "genre" es requerido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_results = int(request.GET.get("max_results", 20))
        order = request.GET.get("order", "relevance")

        # Validar parámetros
        if max_results > 50:
            max_results = 50

        valid_orders = ["relevance", "date", "rating", "viewCount", "title"]
        if order not in valid_orders:
            order = "relevance"

        # Usar el caso de uso
        use_case = SearchMusicByGenreUseCase(GenreRepository())
        result = async_to_sync(use_case.execute)(genre_name, max_results, order)

        if not result["success"]:
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        # Convertir videos a formato JSON serializable
        videos_data = []
        for video in result["videos"]:
            videos_data.append(
                {
                    "id": video.video_id,
                    "title": video.title,
                    "description": video.description,
                    "thumbnail_url": video.thumbnail_url,
                    "duration": video.duration_seconds,
                    "view_count": video.view_count,
                    "like_count": video.like_count,
                    "published_at": (
                        video.published_at.isoformat() if video.published_at else None
                    ),
                    "channel_title": video.channel_title,
                }
            )

        return Response(
            {
                "success": True,
                "genre": result["genre"],
                "total_results": result["total_results"],
                "videos": videos_data,
                "search_parameters": {"max_results": max_results, "order": order},
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        genre_name_safe = request.GET.get("genre", "desconocido")
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": f"Error buscando música del género: {genre_name_safe}",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
