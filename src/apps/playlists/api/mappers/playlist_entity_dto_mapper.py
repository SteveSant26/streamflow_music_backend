"""
Mapper entre entidades de playlist y DTOs
"""

from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper

from ...domain.entities import PlaylistEntity
from ..dtos import PlaylistResponseDTO


class PlaylistEntityDTOMapper(
    AbstractEntityDtoMapper[PlaylistEntity, PlaylistResponseDTO]
):
    """Mapper para convertir entre entidades de playlist y DTOs"""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: PlaylistEntity) -> PlaylistResponseDTO:
        """
        Convierte una entidad PlaylistEntity a PlaylistResponseDTO

        Args:
            entity: Entidad de playlist

        Returns:
            DTO de respuesta de playlist
        """
        self.logger.debug(f"Converting entity to DTO for playlist {entity.id}")

        # Obtener el conteo de canciones
        song_count = self._get_playlist_song_count_sync(entity.id)

        return PlaylistResponseDTO(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            user_id=entity.user_id,
            is_default=entity.is_default,
            is_public=entity.is_public,
            song_count=song_count,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def dto_to_entity(self, dto: PlaylistResponseDTO) -> PlaylistEntity:
        """
        Convierte un PlaylistResponseDTO a PlaylistEntity

        Args:
            dto: DTO de respuesta de playlist

        Returns:
            Entidad de playlist
        """
        self.logger.debug(f"Converting DTO to entity for playlist {dto.id}")

        from datetime import datetime

        return PlaylistEntity(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            user_id=dto.user_id,
            is_default=dto.is_default,
            is_public=dto.is_public,
            created_at=dto.created_at or datetime.now(),
            updated_at=dto.updated_at,
        )

    def _get_playlist_song_count_sync(self, playlist_id: str) -> int:
        """
        Obtiene el número de canciones en una playlist (versión síncrona)

        Args:
            playlist_id: ID de la playlist

        Returns:
            Número de canciones en la playlist
        """
        try:
            from ...infrastructure.models import PlaylistSongModel

            return PlaylistSongModel.objects.filter(playlist_id=playlist_id).count()

        except Exception as e:
            self.logger.error(f"Error obteniendo conteo de canciones: {str(e)}")
            return 0
