from typing import Any, Dict, Iterable, List

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

    def models_to_entities(
        self, models: Iterable[PlaylistSongModel]
    ) -> List[PlaylistSongEntity]:
        """Convierte una lista de PlaylistSongModel a lista de PlaylistSongEntity"""
        return [self.model_to_entity(model) for model in models]

    def entities_to_models(
        self, entities: Iterable[PlaylistSongEntity]
    ) -> List[PlaylistSongModel]:
        """Convierte una lista de PlaylistSongEntity a lista de PlaylistSongModel"""
        return [self.entity_to_model(entity) for entity in entities]

    def bulk_create_from_entities(
        self, entities: List[PlaylistSongEntity]
    ) -> List[PlaylistSongModel]:
        """
        Crea múltiples PlaylistSongModel usando bulk_create para mejor performance.
        Nota: Este método debe usarse dentro de una transacción.
        """
        self.logger.debug(f"Bulk creating {len(entities)} playlist songs")

        models = []
        for entity in entities:
            model = PlaylistSongModel(
                playlist_id=entity.playlist_id,
                song_id=entity.song_id,
                position=entity.position,
                added_at=entity.added_at,
            )
            models.append(model)

        return PlaylistSongModel.objects.bulk_create(models)

    def update_positions(
        self, playlist_id: str, song_positions: List[tuple[str, int]]
    ) -> None:
        """
        Actualiza las posiciones de las canciones en una playlist.
        Nota: Este método debe usarse dentro de una transacción.
        """
        self.logger.debug(f"Updating positions for playlist {playlist_id}")

        # Convertir a diccionario para acceso rápido
        position_map = dict(song_positions)

        # Obtener todas las canciones de la playlist
        playlist_songs = PlaylistSongModel.objects.filter(playlist_id=playlist_id)

        # Actualizar posiciones
        updates = []
        for playlist_song in playlist_songs:
            song_id = str(playlist_song.song.id)
            if song_id in position_map:
                playlist_song.position = position_map[song_id]
                updates.append(playlist_song)

        # Bulk update
        PlaylistSongModel.objects.bulk_update(updates, ["position"])
