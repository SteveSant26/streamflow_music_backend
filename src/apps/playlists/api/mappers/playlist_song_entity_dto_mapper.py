"""
Mapper entre entidades de canción en playlist y DTOs
"""

from typing import Iterable, List

from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper

from ...domain.entities import PlaylistSongEntity
from ..dtos import PlaylistSongResponseDTO


class PlaylistSongEntityDTOMapper(
    AbstractEntityDtoMapper[PlaylistSongEntity, PlaylistSongResponseDTO]
):
    """Mapper para convertir entre entidades de canción en playlist y DTOs"""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: PlaylistSongEntity) -> PlaylistSongResponseDTO:
        """
        Convierte una entidad PlaylistSongEntity a PlaylistSongResponseDTO

        Args:
            entity: Entidad de canción en playlist

        Returns:
            DTO de respuesta de canción en playlist
        """
        self.logger.debug(f"Converting entity to DTO for playlist song {entity.id}")

        # Obtener información de la canción
        song_info = self._get_song_info_sync(entity.song_id)

        return PlaylistSongResponseDTO(
            id=entity.id,
            playlist_id=entity.playlist_id,
            song_id=entity.song_id,
            position=entity.position,
            added_at=entity.added_at,
            song_title=song_info.get("title"),
            song_artist=song_info.get("artist"),
            song_duration=song_info.get("duration"),
        )

    def dto_to_entity(self, dto: PlaylistSongResponseDTO) -> PlaylistSongEntity:
        """
        Convierte un PlaylistSongResponseDTO a PlaylistSongEntity

        Args:
            dto: DTO de respuesta de canción en playlist

        Returns:
            Entidad de canción en playlist
        """
        self.logger.debug(f"Converting DTO to entity for playlist song {dto.id}")

        from datetime import datetime

        return PlaylistSongEntity(
            id=dto.id,
            playlist_id=dto.playlist_id,
            song_id=dto.song_id,
            position=dto.position,
            added_at=dto.added_at or datetime.now(),
        )

    def _get_song_info_sync(self, song_id: str) -> dict:
        """
        Obtiene información básica de una canción (versión síncrona)

        Args:
            song_id: ID de la canción

        Returns:
            Diccionario con información de la canción
        """
        try:
            from apps.songs.infrastructure.models import SongModel

            song = SongModel.objects.select_related("artist").get(id=song_id)

            return {
                "title": song.title,
                "artist": song.artist.name if song.artist else None,
                "duration": song.duration_seconds,
            }

        except Exception as e:
            self.logger.error(f"Error obteniendo información de canción: {str(e)}")
            return {
                "title": None,
                "artist": None,
                "duration": None,
            }

    def entities_to_dtos(
        self, entities: Iterable[PlaylistSongEntity]
    ) -> List[PlaylistSongResponseDTO]:
        """
        Convierte una lista de entidades a DTOs

        Args:
            entities: Lista de entidades de canción en playlist

        Returns:
            Lista de DTOs de respuesta de canción en playlist
        """
        return [self.entity_to_dto(entity) for entity in entities]

    def entities_to_dtos_with_song_info(
        self, entities: Iterable[PlaylistSongEntity]
    ) -> List[PlaylistSongResponseDTO]:
        """
        Convierte entidades a DTOs con información optimizada de canciones
        (usando una sola consulta para todas las canciones)

        Args:
            entities: Lista de entidades de canción en playlist

        Returns:
            Lista de DTOs de respuesta con información de canciones
        """
        entities_list = list(entities)
        if not entities_list:
            return []

        # Obtener IDs de canciones
        song_ids = [entity.song_id for entity in entities_list]

        # Obtener información de todas las canciones en una consulta
        songs_info = self._get_multiple_songs_info_sync(song_ids)

        # Crear DTOs
        dtos = []
        for entity in entities_list:
            song_info = songs_info.get(entity.song_id, {})
            dto = PlaylistSongResponseDTO(
                id=entity.id,
                playlist_id=entity.playlist_id,
                song_id=entity.song_id,
                position=entity.position,
                added_at=entity.added_at,
                song_title=song_info.get("title"),
                song_artist=song_info.get("artist"),
                song_duration=song_info.get("duration"),
            )
            dtos.append(dto)

        return dtos

    def _get_multiple_songs_info_sync(self, song_ids: List[str]) -> dict:
        """
        Obtiene información de múltiples canciones en una sola consulta

        Args:
            song_ids: Lista de IDs de canciones

        Returns:
            Diccionario con información de canciones {song_id: info}
        """
        try:
            from apps.songs.infrastructure.models import SongModel

            songs = SongModel.objects.select_related("artist").filter(id__in=song_ids)

            songs_info = {}
            for song in songs:
                songs_info[str(song.id)] = {
                    "title": song.title,
                    "artist": song.artist.name if song.artist else None,
                    "duration": song.duration_seconds,
                }

            return songs_info

        except Exception as e:
            self.logger.error(
                f"Error obteniendo información de múltiples canciones: {str(e)}"
            )
            return {}
