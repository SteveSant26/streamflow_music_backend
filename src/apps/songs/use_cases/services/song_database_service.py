"""
Servicio para guardar canciones en la base de datos
"""

import logging
from typing import Optional

from ...domain.entities import SongEntity
from ...domain.repository import ISongRepository


class SongDatabaseService:
    """Servicio para operaciones de base de datos de canciones"""

    def __init__(self, song_repository: ISongRepository):
        self.logger = logging.getLogger(__name__)
        self.song_repository = song_repository

    async def save_song_to_database(
        self, song_entity: SongEntity, title: str
    ) -> Optional[SongEntity]:
        """
        Guarda la canción en la base de datos

        Args:
            song_entity: Entidad de canción a guardar
            title: Título de la canción para logs

        Returns:
            Entidad guardada o None si falla
        """
        try:
            saved_song = await self.song_repository.save(song_entity)

            if saved_song:
                self.logger.info(
                    f"✅ Successfully saved song '{title}' to database with ID: {saved_song.id}"
                )
            else:
                self.logger.error(f"❌ Failed to save song '{title}' to database")

            return saved_song

        except Exception as e:
            self.logger.error(f"❌ Exception saving song '{title}': {str(e)}")
            return None
