"""
Servicio simplificado para gestión de géneros musicales.
Enfocado en operaciones básicas, el análisis automático se maneja en apps/genres.
"""

import logging
from typing import List, Optional

from django.conf import settings

from ...types.media_types import SearchOptions, YouTubeVideoInfo
from ..media.youtube_service import YouTubeAPIService


class MusicGenreService:
    """Servicio simplificado para operaciones básicas de géneros"""

    def __init__(self, youtube_service: Optional[YouTubeAPIService] = None):
        self.logger = logging.getLogger(__name__)
        self.youtube_service = youtube_service or YouTubeAPIService()

    def get_predefined_genres(self) -> dict:
        """Obtiene géneros predefinidos desde configuración"""
        return getattr(settings, "YOUTUBE_MUSIC_GENRES", {})

    async def search_music_by_genre(
        self, genre_name: str, max_results: int = 20, order: str = "relevance"
    ) -> List[YouTubeVideoInfo]:
        """Busca música de un género específico"""
        try:
            # Construir query optimizada
            search_query = f"{genre_name} music"

            search_options = SearchOptions(
                max_results=max_results,
                video_category_id="10",  # Solo música
                order=order,
                safe_search="moderate",
            )

            # Buscar usando el servicio de YouTube
            videos = await self.youtube_service.search_music_only(
                search_query, search_options
            )

            return videos

        except Exception as e:
            self.logger.error(f"Error searching music by genre '{genre_name}': {e}")
            return []

    def get_genre_keywords(self, genre_name: str) -> List[str]:
        """Obtiene palabras clave para un género específico"""
        genres_config = self.get_predefined_genres()

        for genre_key, genre_data in genres_config.items():
            if genre_data.get("name", "").lower() == genre_name.lower():
                return genre_data.get("keywords", [])

        # Fallback: generar palabras clave básicas
        return [genre_name.lower(), f"{genre_name.lower()} music"]
