"""
Servicio para manejo de géneros en canciones.
Se encarga de analizar y asignar géneros automáticamente cuando se procesa música nueva.
"""

import logging
from typing import Any, Dict, Optional

from apps.genres.infrastructure.models import GenreModel
from apps.genres.services.music_genre_analyzer import MusicGenreAnalyzer
from apps.songs.infrastructure.models import SongModel

logger = logging.getLogger(__name__)


class SongGenreService:
    """Servicio para asignar géneros automáticamente a las canciones"""

    def __init__(self):
        self.genre_analyzer = MusicGenreAnalyzer()

    async def assign_genres_to_song(
        self,
        song: SongModel,
        video_info: Optional[Dict[str, Any]] = None,
        force_reanalysis: bool = False,
    ) -> bool:
        """
        Asigna géneros automáticamente a una canción basándose en su metadata.

        Args:
            song: Instancia del modelo de canción
            video_info: Información del video (si viene de YouTube)
            force_reanalysis: Si True, reanaliza aunque ya tenga géneros

        Returns:
            bool: True si se asignaron géneros exitosamente
        """
        try:
            # Si ya tiene géneros y no se fuerza el reanálisis, saltar
            if not force_reanalysis and song.genres.exists():
                logger.debug(f"Canción '{song.title}' ya tiene géneros asignados")
                return True

            # Usar el analizador mejorado para obtener géneros
            if video_info:
                # Si tenemos info de YouTube, usar el método principal
                from types import SimpleNamespace

                youtube_info = SimpleNamespace(
                    title=song.title,
                    description=video_info.get("description", ""),
                    tags=video_info.get("tags", []),
                    channel_title=video_info.get(
                        "channel_title", song.artist_name or ""
                    ),
                )
                genre_matches = await self.genre_analyzer.analyze_music_genres(youtube_info)  # type: ignore
            else:
                # Usar metadata básica
                genre_matches = await self.genre_analyzer.analyze_music_from_metadata(
                    title=song.title,
                    artist=song.artist_name or "",
                    album=song.album_title or "",
                    tags=[],
                    max_genres=3,
                    min_confidence=0.2,
                )

            if not genre_matches:
                logger.warning(f"No se pudieron determinar géneros para '{song.title}'")
                return False

            # Convertir GenreMatch a GenreModel
            genre_objects = []
            for match in genre_matches:
                try:
                    # Buscar el modelo correspondiente por el ID de la entidad
                    genre_model = GenreModel.objects.get(id=match.genre.id)
                    genre_objects.append(genre_model)
                except GenreModel.DoesNotExist:
                    logger.warning(f"Género {match.genre.name} no encontrado en la BD")

            if not genre_objects:
                logger.warning(f"No se encontraron modelos válidos para '{song.title}'")
                return False

            # Asignar géneros a la canción
            song.genres.set(genre_objects)
            song.genre_names = [genre.name for genre in genre_objects]
            song.save(update_fields=["genre_names"])

            logger.info(
                f"Géneros asignados a '{song.title}': "
                f"{', '.join([g.name for g in genre_objects])}"
            )
            return True

        except Exception as e:
            logger.error(f"Error asignando géneros a '{song.title}': {str(e)}")
            return False
