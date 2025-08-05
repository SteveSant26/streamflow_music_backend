"""
Procesador para crear entidades de canciones
"""
import logging
from typing import List, Optional

from ....music_search.domain.interfaces import MusicTrackData
from ...domain.entities import SongEntity
from ...infrastructure.mappers.track_to_song_entity_mapper import (
    TrackToSongEntityMapper,
)


class SongEntityProcessor:
    """Procesador para crear entidades de canciones"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mapper = TrackToSongEntityMapper()

    async def create_song_entity(
        self,
        music_track: MusicTrackData,
        file_url: Optional[str],
        updated_thumbnail_url: Optional[str],
        analyzed_genres: List[str],
        artist_album_info: dict,
    ) -> SongEntity:
        """
        Crea la entidad de canción con toda la información procesada

        Args:
            music_track: Datos del track de música
            file_url: URL del archivo de audio
            updated_thumbnail_url: URL del thumbnail
            analyzed_genres: Lista de géneros analizados
            artist_album_info: Información de artista y álbum

        Returns:
            Entidad de canción creada
        """
        artist_id = artist_album_info.get("artist_id")
        album_id = artist_album_info.get("album_id")
        artist_name = artist_album_info.get("artist_name") or music_track.artist_name
        album_title = artist_album_info.get("album_title") or music_track.album_title

        # Crear entidad usando el mapper
        song_entity = await self.mapper.map(
            music_track,
            file_url=file_url,
            thumbnail_url=updated_thumbnail_url,
            analyzed_genres=analyzed_genres,
            artist_id=artist_id,
            album_id=album_id,
        )

        # Actualizar información desnormalizada
        if artist_name:
            song_entity.artist_name = artist_name
        if album_title:
            song_entity.album_title = album_title

        # Logs informativos
        self._log_song_entity_creation(
            song_entity,
            music_track.title,
            artist_name,
            album_title,
            artist_id,
            album_id,
        )

        return song_entity

    def _log_song_entity_creation(
        self,
        song_entity: SongEntity,
        title: str,
        artist_name: Optional[str],
        album_title: Optional[str],
        artist_id: Optional[str],
        album_id: Optional[str],
    ):
        """Logs informativos para la creación de la entidad"""
        self.logger.debug(
            f"Song entity created with artist_id: {song_entity.artist_id}, album_id: {song_entity.album_id}"
        )
        self.logger.info(
            f"🎵 Created song entity '{title}' with {len(song_entity.genre_ids or [])} genre(s): {song_entity.genre_ids}"
        )
        if artist_id:
            self.logger.info(f"   🎤 Artist: {artist_name} (ID: {artist_id})")
        if album_id:
            self.logger.info(f"   💿 Album: {album_title} (ID: {album_id})")
