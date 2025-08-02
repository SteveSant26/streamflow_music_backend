"""
Caso de uso para buscar música por género utilizando la API de YouTube.
"""

import logging
from typing import Optional

from src.common.adapters.media.youtube_service import YouTubeAPIService
from src.common.types.media_types import SearchOptions

from ..domain.entities import GenreEntity
from ..domain.repository.Igenre_repository import IGenreRepository


class SearchMusicByGenreUseCase:
    """Caso de uso para buscar música por género"""

    def __init__(
        self,
        genre_repository: IGenreRepository,
        youtube_service: Optional[YouTubeAPIService] = None,
    ):
        self.genre_repository = genre_repository
        self.youtube_service = youtube_service or YouTubeAPIService()
        self.logger = logging.getLogger(__name__)

    async def execute(
        self, genre_name: str, max_results: int = 20, order: str = "relevance"
    ) -> dict:
        """
        Busca música por género específico.

        Args:
            genre_name: Nombre del género musical
            max_results: Número máximo de resultados
            order: Orden de los resultados

        Returns:
            Dict con información del género y videos encontrados
        """
        try:
            # Buscar el género en la base de datos
            genres = await self.genre_repository.search_by_name(genre_name, limit=1)

            if not genres:
                self.logger.warning(
                    f"Género '{genre_name}' no encontrado en la base de datos"
                )
                return {
                    "success": False,
                    "error": f"Género '{genre_name}' no encontrado",
                    "genre": None,
                    "videos": [],
                }

            genre = genres[0]
            self.logger.info(f"Buscando música para el género: {genre.name}")

            # Configurar opciones de búsqueda
            search_options = SearchOptions(
                max_results=max_results,
                order=order,
                video_category_id="10",  # Categoría de música en YouTube
                safe_search="moderate",
            )

            # Buscar videos usando el servicio de YouTube
            videos = await self.youtube_service.search_videos(
                query=f"{genre.name} music", options=search_options
            )

            # Actualizar popularidad del género
            await self._update_genre_popularity(genre, len(videos))

            return {
                "success": True,
                "genre": {
                    "id": genre.id,
                    "name": genre.name,
                    "description": genre.description,
                    "popularity_score": genre.popularity_score,
                },
                "videos": videos,
                "total_results": len(videos),
            }

        except Exception as e:
            self.logger.error(
                f"Error buscando música por género '{genre_name}': {str(e)}"
            )
            return {"success": False, "error": str(e), "genre": None, "videos": []}

    async def _update_genre_popularity(self, genre: GenreEntity, video_count: int):
        """Actualiza la popularidad del género basado en los resultados"""
        try:
            # Incrementar score basado en resultados encontrados
            new_score = genre.popularity_score + min(video_count, 10)
            genre.popularity_score = new_score

            await self.genre_repository.update(genre.id, genre)
            self.logger.debug(
                f"Actualizada popularidad de '{genre.name}' a {new_score}"
            )

        except Exception as e:
            self.logger.warning(f"Error actualizando popularidad de género: {str(e)}")
