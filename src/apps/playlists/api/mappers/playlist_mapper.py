from apps.playlists.api.mappers.playlist_entity_dto_mapper import PlaylistEntityDtoMapper
from apps.playlists.api.mappers.playlist_entity_model_mapper import PlaylistEntityModelMapper
from common.interfaces.imapper.abstract_mapper import AbstractMapper


class PlaylistMapper(AbstractMapper):
    """Mapper completo para playlists que combina model-entity y entity-dto"""
    
    def __init__(self):
        super().__init__()
        self._model_entity_mapper = PlaylistEntityModelMapper()
        self._entity_dto_mapper = PlaylistEntityDtoMapper()
