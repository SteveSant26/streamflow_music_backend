"""
Servicio simplificado para gestión de géneros musicales.
Se enfoca únicamente en buscar música por género usando YouTube API.
La clasificación y análisis de géneros se maneja en apps/genres con MusicGenreAnalyzer.
"""

from typing import List, Optional

from ...mixins.logging_mixin import LoggingMixin
from ...types.media_types import SearchOptions, YouTubeVideoInfo
from ..media.youtube_service import YouTubeAPIService


class MusicGenreService(LoggingMixin):
    """Servicio simplificado para búsqueda de música por género"""

    def __init__(self, youtube_service: Optional[YouTubeAPIService] = None):
        super().__init__()
        self.youtube_service = youtube_service or YouTubeAPIService()

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
        """Genera palabras clave básicas para búsqueda de un género específico"""
        # Generar palabras clave básicas para búsqueda
        base_keywords = [genre_name.lower(), f"{genre_name.lower()} music"]

        # Agregar variaciones comunes
        if " " in genre_name:
            # Para géneros compuestos como "Hip Hop"
            base_keywords.append(genre_name.lower().replace(" ", ""))

        return base_keywords
