from typing import Any, Dict

from apps.playlists.domain.entities import PlaylistSongEntity
from apps.playlists.infrastructure.models import PlaylistSongModel
from common.interfaces.imapper.abstract_model_entity_mapper import (
    AbstractEntityModelMapper,
)


class PlaylistSongEntityModelMapper(
    AbstractEntityModelMapper[PlaylistSongEntity, PlaylistSongModel]
):
    """Mapper entre PlaylistSongModel y PlaylistSongEntity"""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: PlaylistSongModel) -> PlaylistSongEntity:
        """Convierte un PlaylistSongModel a PlaylistSongEntity"""
        self.logger.debug(f"Converting model to entity for playlist song {model.id}")

        return PlaylistSongEntity(
            id=str(model.id),
            playlist_id=str(model.playlist.id),
            song_id=str(model.song.id),
            position=model.position,
            added_at=model.added_at,
        )

    def entity_to_model(self, entity: PlaylistSongEntity) -> PlaylistSongModel:
        """Convierte una PlaylistSongEntity a PlaylistSongModel"""
        self.logger.debug(f"Converting entity to model for playlist song {entity.id}")

        return PlaylistSongModel(
            id=entity.id,
            playlist_id=entity.playlist_id,
            song_id=entity.song_id,
            position=entity.position,
            added_at=entity.added_at,
        )

    def entity_to_model_data(self, entity: PlaylistSongEntity) -> Dict[str, Any]:
        """Convierte una PlaylistSongEntity a datos para PlaylistSongModel"""
        self.logger.debug(
            f"Converting entity to model data for playlist song {entity.id}"
        )

        return {
            "id": entity.id,
            "playlist_id": entity.playlist_id,
            "song_id": entity.song_id,
            "position": entity.position,
            "added_at": entity.added_at,
        }
