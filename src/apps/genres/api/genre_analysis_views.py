"""
API Views para análisis automático de géneros musicales.
"""

import asyncio
import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from src.common.adapters.media.youtube_service import YouTubeAPIService

from ..use_cases.analyze_music_genres_use_case import (
    AnalyzeMusicGenresUseCase,
    ValidateGenreClassificationUseCase,
)

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def analyze_music_genres(request):
    """
    Analiza una música y determina qué géneros le corresponden automáticamente.

    Body Parameters:
    - video_id: str (required) - ID del video de YouTube
    - max_genres: int (default: 3) - Máximo número de géneros a retornar
    - min_confidence: float (default: 0.3) - Confianza mínima (0.0-1.0)
    """
    try:
        # Validar parámetros de entrada
        video_id = request.data.get("video_id")
        if not video_id:
            return Response(
                {"success": False, "error": 'El parámetro "video_id" es requerido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_genres = int(request.data.get("max_genres", 3))
        min_confidence = float(request.data.get("min_confidence", 0.3))

        # Validar rangos
        if max_genres < 1 or max_genres > 10:
            max_genres = 3
        if min_confidence < 0.0 or min_confidence > 1.0:
            min_confidence = 0.3

        # Obtener información del video desde YouTube
        youtube_service = YouTubeAPIService()

        async def get_video_and_analyze():
            # Obtener detalles del video
            video_info = await youtube_service.get_video_details(video_id)

            if not video_info:
                return {
                    "success": False,
                    "error": f"No se pudo obtener información del video: {video_id}",
                    "video_id": video_id,
                }

            # Analizar géneros
            use_case = AnalyzeMusicGenresUseCase()
            result = await use_case.execute(video_info, max_genres, min_confidence)

            return result

        result = asyncio.run(get_video_and_analyze())

        if result["success"]:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)

    except ValueError as e:
        return Response(
            {
                "success": False,
                "error": f"Parámetros inválidos: {str(e)}",
                "message": "Verifica que max_genres sea un entero y min_confidence un decimal",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Error durante el análisis de géneros",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def batch_analyze_genres(request):
    """
    Analiza múltiples músicas en lote para identificar géneros.

    Body Parameters:
    - video_ids: List[str] (required) - Lista de IDs de videos de YouTube
    - max_genres: int (default: 2) - Máximo número de géneros por canción
    - min_confidence: float (default: 0.4) - Confianza mínima
    """
    try:
        video_ids = request.data.get("video_ids", [])
        if not video_ids or not isinstance(video_ids, list):
            return Response(
                {
                    "success": False,
                    "error": 'El parámetro "video_ids" debe ser una lista no vacía',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(video_ids) > 50:  # Limitar para evitar sobrecarga
            return Response(
                {"success": False, "error": "Máximo 50 videos por lote"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_genres = int(request.data.get("max_genres", 2))
        min_confidence = float(request.data.get("min_confidence", 0.4))

        # Validar rangos
        if max_genres < 1 or max_genres > 5:
            max_genres = 2
        if min_confidence < 0.0 or min_confidence > 1.0:
            min_confidence = 0.4

        async def get_videos_and_analyze():
            youtube_service = YouTubeAPIService()
            music_list = []

            # Obtener información de todos los videos
            for video_id in video_ids:
                try:
                    video_info = await youtube_service.get_video_details(video_id)
                    if video_info:
                        music_list.append(video_info)
                except Exception as e:
                    # Log error for debugging but continue with next video
                    logger.warning(
                        f"Failed to get video details for {video_id}: {str(e)}"
                    )
                    continue  # Continuar con los siguientes videos

            if not music_list:
                return {
                    "success": False,
                    "error": "No se pudo obtener información de ningún video",
                    "video_ids": video_ids,
                }

            # Analizar en lote
            use_case = AnalyzeMusicGenresUseCase()
            result = await use_case.batch_analyze(
                music_list, max_genres, min_confidence
            )

            return result

        result = asyncio.run(get_videos_and_analyze())

        return Response(result, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response(
            {"success": False, "error": f"Parámetros inválidos: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Error durante el análisis en lote",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def validate_genre_classification(request):
    """
    Valida si una música realmente pertenece al género especificado.

    Body Parameters:
    - video_id: str (required) - ID del video de YouTube
    - expected_genre: str (required) - Género esperado
    """
    try:
        video_id = request.data.get("video_id")
        expected_genre = request.data.get("expected_genre")

        if not video_id:
            return Response(
                {"success": False, "error": 'El parámetro "video_id" es requerido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not expected_genre:
            return Response(
                {
                    "success": False,
                    "error": 'El parámetro "expected_genre" es requerido',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        async def get_video_and_validate():
            # Obtener información del video
            youtube_service = YouTubeAPIService()
            video_info = await youtube_service.get_video_details(video_id)

            if not video_info:
                return {
                    "success": False,
                    "error": f"No se pudo obtener información del video: {video_id}",
                    "video_id": video_id,
                }

            # Validar clasificación
            use_case = ValidateGenreClassificationUseCase()
            result = await use_case.execute(video_info, expected_genre)

            return {"success": True, "validation": result}

        result = asyncio.run(get_video_and_validate())

        if result["success"]:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Error durante la validación de género",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def get_genre_analysis_stats(request):
    """
    Obtiene estadísticas del sistema de análisis de géneros.
    """
    try:
        from ..services.genre_service import GenreService

        async def get_stats():
            genre_service = GenreService()

            # Obtener géneros más populares
            popular_genres = await genre_service.get_popular_genres(limit=10)

            # Obtener total de géneros
            all_genres = await genre_service.get_all_genres()

            stats = {
                "total_genres": len(all_genres),
                "active_genres": len([g for g in all_genres if g.is_active]),
                "most_popular_genres": [
                    {
                        "name": genre.name,
                        "popularity_score": genre.popularity_score,
                        "description": genre.description,
                    }
                    for genre in popular_genres
                ],
                "genre_categories": {},
            }

            # Agrupar por categorías (basado en descripción)
            categories = {}
            for genre in all_genres:
                if genre.description:
                    # Extraer categoría de la descripción
                    if "Pop" in genre.description:
                        category = "Pop"
                    elif "Rock" in genre.description:
                        category = "Rock"
                    elif "Electronic" in genre.description:
                        category = "Electronic"
                    elif "Hip Hop" in genre.description:
                        category = "Hip Hop"
                    elif "Latin" in genre.description:
                        category = "Latin"
                    else:
                        category = "Other"

                    if category not in categories:
                        categories[category] = 0
                    categories[category] += 1

            stats["genre_categories"] = categories

            return stats

        stats = asyncio.run(get_stats())

        return Response(
            {"success": True, "statistics": stats}, status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Error obteniendo estadísticas",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
