"""
API Views para el sistema de géneros musicales de YouTube.

Proporciona endpoints para obtener, buscar y analizar géneros musicales.
"""

import asyncio
import json

from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from src.common.adapters.media.youtube_service import YouTubeAPIService
from src.common.adapters.music.genre_service import MusicGenreService


class MusicGenresAPIView(View):
    """Vista base para el API de géneros musicales"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.genre_service = MusicGenreService()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_all_genres(request):
    """
    Obtiene todos los géneros musicales disponibles.

    Query Parameters:
    - include_analytics: bool (default: false) - Incluir análisis de popularidad
    - force_refresh: bool (default: false) - Forzar actualización de caché
    - category: str (optional) - Filtrar por categoría específica
    """
    try:
        # Obtener parámetros de consulta
        include_analytics = (
            request.GET.get("include_analytics", "false").lower() == "true"
        )
        force_refresh = request.GET.get("force_refresh", "false").lower() == "true"
        category_filter = request.GET.get("category")

        # Crear servicio y obtener géneros
        genre_service = MusicGenreService()

        async def get_genres():
            if category_filter:
                return await genre_service.get_genres_by_category(category_filter)
            else:
                return await genre_service.get_all_available_genres(
                    include_analytics=include_analytics, force_refresh=force_refresh
                )

        # Ejecutar función asíncrona
        genres = asyncio.run(get_genres())

        # Convertir a formato JSON serializable
        genres_data = []
        for genre in genres:
            genre_dict = {
                "name": genre.name,
                "category": genre.category,
                "keywords": genre.keywords,
                "popularity_score": genre.popularity_score,
                "video_count": genre.video_count,
                "sample_videos": genre.sample_videos or [],
                "last_updated": genre.last_updated.isoformat()
                if genre.last_updated
                else None,
            }
            genres_data.append(genre_dict)

        response_data = {
            "success": True,
            "total_genres": len(genres_data),
            "genres": genres_data,
            "metadata": {
                "include_analytics": include_analytics,
                "category_filter": category_filter,
                "cache_refreshed": force_refresh,
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Error obteniendo géneros musicales",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_genre_categories(request):
    """
    Obtiene las categorías de géneros musicales disponibles.
    """
    try:
        genre_service = MusicGenreService()

        async def get_categories():
            all_genres = await genre_service.get_all_available_genres()
            categories = {}

            for genre in all_genres:
                category = genre.category
                if category not in categories:
                    categories[category] = {
                        "name": category,
                        "genre_count": 0,
                        "genres": [],
                    }

                categories[category]["genre_count"] += 1
                categories[category]["genres"].append(
                    {"name": genre.name, "popularity_score": genre.popularity_score}
                )

            # Ordenar géneros dentro de cada categoría por popularidad
            for category_data in categories.values():
                category_data["genres"].sort(
                    key=lambda x: x["popularity_score"], reverse=True
                )

            return list(categories.values())

        categories = asyncio.run(get_categories())

        return Response(
            {
                "success": True,
                "total_categories": len(categories),
                "categories": categories,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Error obteniendo categorías de géneros",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def search_music_by_genre(request):
    """
    Busca música por género específico.

    Query Parameters:
    - genre: str (required) - Nombre del género
    - max_results: int (default: 20) - Número máximo de resultados
    - order: str (default: relevance) - Orden de resultados (relevance, date, rating, viewCount)
    """
    try:
        genre_name = request.GET.get("genre")
        if not genre_name:
            return Response(
                {"success": False, "error": 'El parámetro "genre" es requerido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_results = int(request.GET.get("max_results", 20))
        order = request.GET.get("order", "relevance")

        # Validar parámetros
        if max_results > 50:
            max_results = 50  # Límite de la API

        valid_orders = ["relevance", "date", "rating", "viewCount", "title"]
        if order not in valid_orders:
            order = "relevance"

        genre_service = MusicGenreService()

        async def search_genre():
            return await genre_service.search_music_by_genre(
                genre_name=genre_name, max_results=max_results, order=order
            )

        videos = asyncio.run(search_genre())

        # Convertir videos a formato JSON serializable
        videos_data = []
        for video in videos:
            video_dict = {
                "video_id": video.video_id,
                "title": video.title,
                "channel_title": video.channel_title,
                "channel_id": video.channel_id,
                "thumbnail_url": video.thumbnail_url,
                "duration_seconds": video.duration_seconds,
                "published_at": video.published_at.isoformat(),
                "view_count": video.view_count,
                "like_count": video.like_count,
                "genre": video.genre,
                "url": video.url,
                "tags": video.tags[:10],  # Limitar tags para reducir tamaño
            }
            videos_data.append(video_dict)

        return Response(
            {
                "success": True,
                "genre": genre_name,
                "total_results": len(videos_data),
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
def analyze_genre_popularity(request):
    """
    Analiza la popularidad de un género específico.

    Query Parameters:
    - genre: str (required) - Nombre del género a analizar
    """
    try:
        genre_name = request.GET.get("genre")
        if not genre_name:
            return Response(
                {"success": False, "error": 'El parámetro "genre" es requerido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        genre_service = MusicGenreService()

        async def analyze_genre():
            return await genre_service.analyze_genre_popularity(genre_name)

        analytics = asyncio.run(analyze_genre())

        analytics_data = {
            "genre_name": analytics.genre_name,
            "total_views": analytics.total_views,
            "average_views": analytics.average_views,
            "total_likes": analytics.total_likes,
            "average_likes": analytics.average_likes,
            "video_count": analytics.video_count,
            "trending_score": analytics.trending_score,
            "peak_popularity_period": analytics.peak_popularity_period,
        }

        return Response(
            {"success": True, "analytics": analytics_data}, status=status.HTTP_200_OK
        )

    except Exception as e:
        genre_name_safe = request.GET.get("genre", "desconocido")
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": f"Error analizando popularidad del género: {genre_name_safe}",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_trending_genres(request):
    """
    Obtiene los géneros más populares actualmente.

    Query Parameters:
    - limit: int (default: 10) - Número de géneros a retornar
    """
    try:
        limit = int(request.GET.get("limit", 10))
        if limit > 20:
            limit = 20  # Límite para evitar sobrecarga

        genre_service = MusicGenreService()

        async def get_trending():
            return await genre_service.get_trending_genres(limit=limit)

        trending_data = asyncio.run(get_trending())

        # Convertir datos de trending
        trending_genres = []
        for genre_info, analytics in trending_data:
            trending_item = {
                "genre": {
                    "name": genre_info.name,
                    "category": genre_info.category,
                    "keywords": genre_info.keywords,
                },
                "analytics": {
                    "trending_score": analytics.trending_score,
                    "total_views": analytics.total_views,
                    "video_count": analytics.video_count,
                    "average_views": analytics.average_views,
                },
            }
            trending_genres.append(trending_item)

        return Response(
            {
                "success": True,
                "total_trending": len(trending_genres),
                "trending_genres": trending_genres,
                "metadata": {
                    "limit": limit,
                    "analysis_date": asyncio.get_event_loop().time(),
                },
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Error obteniendo géneros trending",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_youtube_music_categories(request):
    """
    Obtiene las categorías oficiales de YouTube relacionadas con música.
    """
    try:
        youtube_service = YouTubeAPIService()

        async def get_categories():
            return await youtube_service.get_music_categories()

        categories = asyncio.run(get_categories())

        return Response(
            {
                "success": True,
                "total_categories": len(categories),
                "music_categories": categories,
                "quota_usage": youtube_service.get_quota_usage(),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Error obteniendo categorías de YouTube",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def validate_music_content(request):
    """
    Valida si un video de YouTube corresponde a un género musical específico.

    Body Parameters:
    - video_id: str (required) - ID del video de YouTube
    - expected_genre: str (required) - Género esperado
    """
    try:
        data = json.loads(request.body)
        video_id = data.get("video_id")
        expected_genre = data.get("expected_genre")

        if not video_id or not expected_genre:
            return Response(
                {
                    "success": False,
                    "error": 'Los parámetros "video_id" y "expected_genre" son requeridos',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        youtube_service = YouTubeAPIService()
        genre_service = MusicGenreService()

        async def validate_content():
            # Obtener detalles del video
            video = await youtube_service.get_video_details(video_id)
            if not video:
                raise Exception(f"No se pudo obtener información del video: {video_id}")

            # Validar género
            validation = await genre_service.validate_music_content_by_genre(
                video, expected_genre
            )

            return video, validation

        video, validation_result = asyncio.run(validate_content())

        # Agregar información del video a la respuesta
        video_info = {
            "video_id": video.video_id,
            "title": video.title,
            "channel_title": video.channel_title,
            "genre": video.genre,
            "category_id": video.category_id,
            "tags": video.tags[:10],
        }

        return Response(
            {
                "success": True,
                "video_info": video_info,
                "validation": validation_result,
                "expected_genre": expected_genre,
            },
            status=status.HTTP_200_OK,
        )

    except json.JSONDecodeError:
        return Response(
            {"success": False, "error": "JSON inválido en el cuerpo de la petición"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Error validando contenido musical",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
