from apps.playlists.api.mappers import (
    PlaylistEntityDTOMapper,
    PlaylistEntityModelMapper,
)
from common.interfaces.imapper.abstract_mapper import AbstractMapper


class PlaylistMapper(
    PlaylistEntityModelMapper,
    PlaylistEntityDTOMapper,
    AbstractMapper,
):
    """Mapper completo para playlists que combina model-entity y entity-dto"""

    def __init__(self):
        super().__init__()
