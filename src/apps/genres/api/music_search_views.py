"""
API Views adicionales para búsqueda de música por géneros.
"""

import asyncio

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..infrastructure.repository.genre_repository import GenreRepository
from ..services.genre_service import GenreService
from ..use_cases.search_music_by_genre_use_case import SearchMusicByGenreUseCase


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

        async def search():
            return await use_case.execute(genre_name, max_results, order)

        result = asyncio.run(search())

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
                    "published_at": video.published_at.isoformat()
                    if video.published_at
                    else None,
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


@api_view(["GET"])
@permission_classes([AllowAny])
def get_popular_genres_api(request):
    """
    Obtiene los géneros más populares.

    Query Parameters:
    - limit: int (default: 10) - Número máximo de resultados
    """
    try:
        limit = int(request.GET.get("limit", 10))
        if limit > 50:
            limit = 50

        genre_service = GenreService()

        async def get_popular():
            return await genre_service.get_popular_genres(limit=limit)

        genres = asyncio.run(get_popular())

        genres_data = [
            {
                "id": genre.id,
                "name": genre.name,
                "description": genre.description,
                "popularity_score": genre.popularity_score,
                "is_active": genre.is_active,
            }
            for genre in genres
        ]

        return Response(
            {"success": True, "total": len(genres_data), "genres": genres_data},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Error obteniendo géneros populares",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def search_genres_api(request):
    """
    Busca géneros por nombre en la base de datos.

    Query Parameters:
    - name: str (required) - Nombre del género a buscar
    - limit: int (default: 10) - Número máximo de resultados
    """
    try:
        name = request.GET.get("name")
        if not name:
            return Response(
                {"success": False, "error": 'Parámetro "name" es requerido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        limit = int(request.GET.get("limit", 10))
        genre_service = GenreService()

        async def search():
            return await genre_service.search_genres(name, limit=limit)

        genres = asyncio.run(search())

        genres_data = [
            {
                "id": genre.id,
                "name": genre.name,
                "description": genre.description,
                "popularity_score": genre.popularity_score,
            }
            for genre in genres
        ]

        return Response(
            {
                "success": True,
                "search_term": name,
                "total": len(genres_data),
                "genres": genres_data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"success": False, "error": str(e), "message": "Error buscando géneros"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
