from apps.playlists.api.mappers import (
    PlaylistSongEntityDTOMapper,
    PlaylistSongEntityModelMapper,
)
from common.interfaces.imapper.abstract_mapper import AbstractMapper


class PlaylistSongMapper(
    PlaylistSongEntityModelMapper,
    PlaylistSongEntityDTOMapper,
    AbstractMapper,
):
    """Mapper completo para playlists que combina model-entity y entity-dto"""

    def __init__(self):
        super().__init__()
