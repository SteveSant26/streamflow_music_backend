"""
Mapper entre entidades de canción en playlist y DTOs
"""

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
