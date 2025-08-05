from typing import Any, Dict, List

from apps.playlists.api.dtos.playlist_dtos import PlaylistResponseDTO
from apps.playlists.api.mappers.playlist_entity_dto_mapper import (
    PlaylistEntityDTOMapper,
)
from apps.playlists.api.mappers.playlist_entity_model_mapper import (
    PlaylistEntityModelMapper,
)
from apps.playlists.domain.entities import PlaylistEntity
from apps.playlists.infrastructure.models import PlaylistModel


class PlaylistMapper:
    """Mapper completo para playlists que combina model-entity y entity-dto"""

    def __init__(self):
        from common.utils.logging_helper import add_logging_to_instance

        add_logging_to_instance(self)
        self._model_entity_mapper = PlaylistEntityModelMapper()
        self._entity_dto_mapper = PlaylistEntityDTOMapper()

    def model_to_entity(self, model: PlaylistModel) -> PlaylistEntity:
        """Convierte un PlaylistModel a PlaylistEntity"""
        return self._model_entity_mapper.model_to_entity(model)

    def entity_to_dto(self, entity: PlaylistEntity) -> PlaylistResponseDTO:
        """Convierte una PlaylistEntity a PlaylistResponseDTO"""
        return self._entity_dto_mapper.entity_to_dto(entity)

    def entities_to_dtos(
        self, entities: List[PlaylistEntity]
    ) -> List[PlaylistResponseDTO]:
        """Convierte una lista de PlaylistEntity a PlaylistResponseDTO"""
        return [self._entity_dto_mapper.entity_to_dto(entity) for entity in entities]

    def entity_to_model_data(self, entity: PlaylistEntity) -> Dict[str, Any]:
        """Convierte una PlaylistEntity a datos para PlaylistModel"""
        return self._model_entity_mapper.entity_to_model_data(entity)
