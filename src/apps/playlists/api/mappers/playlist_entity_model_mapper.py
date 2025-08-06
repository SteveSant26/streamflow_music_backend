from typing import Any, Dict, List

from apps.playlists.domain.entities import PlaylistEntity, PlaylistSongEntity
from apps.playlists.infrastructure.models import PlaylistModel, PlaylistSongModel
from common.interfaces.imapper.abstract_model_entity_mapper import (
    AbstractEntityModelMapper,
)


class PlaylistEntityModelMapper(
    AbstractEntityModelMapper[PlaylistEntity, PlaylistModel]
):
    """Mapper entre PlaylistModel y PlaylistEntity"""

    def __init__(self):
        super().__init__()

    def model_to_entity(
        self, model: PlaylistModel, include_songs: bool = False
    ) -> PlaylistEntity:
        """Convierte un PlaylistModel a PlaylistEntity"""
        self.logger.debug(f"Converting model to entity for playlist {model.id}")

        songs = None
        if include_songs:
            songs = self._convert_playlist_songs_to_entities(model)

        return PlaylistEntity(
            id=str(model.id),
            name=model.name,
            description=model.description,
            user_id=str(model.user.id),
            is_default=model.is_default,
            is_public=model.is_public,
            created_at=model.created_at,
            updated_at=model.updated_at,
            songs=songs,
        )

    def entity_to_model(self, entity: PlaylistEntity) -> PlaylistModel:
        """Convierte una PlaylistEntity a PlaylistModel"""
        self.logger.debug(f"Converting entity to model for playlist {entity.id}")

        return PlaylistModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            user_id=entity.user_id,
            is_default=entity.is_default,
            is_public=entity.is_public,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def entity_to_model_data(self, entity: PlaylistEntity) -> Dict[str, Any]:
        """Convierte una PlaylistEntity a datos para PlaylistModel"""
        self.logger.debug(f"Converting entity to model data for playlist {entity.id}")

        return {
            "id": entity.id,
            "name": entity.name,
            "description": entity.description,
            "user_id": entity.user_id,  # Usar user_id para la creación
            "is_default": entity.is_default,
            "is_public": entity.is_public,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def _convert_playlist_songs_to_entities(
        self, model: PlaylistModel
    ) -> List[PlaylistSongEntity]:
        """Convierte las canciones de la playlist a entidades"""
        songs = []
        for playlist_song in model.playlist_songs.select_related("song").order_by(
            "position"
        ):
            song_entity = PlaylistSongEntity(
                id=str(playlist_song.id),
                playlist_id=str(playlist_song.playlist.id),
                song_id=str(playlist_song.song.id),
                position=playlist_song.position,
                added_at=playlist_song.added_at,
            )
            songs.append(song_entity)
        return songs

    def create_playlist_with_songs(self, entity: PlaylistEntity) -> PlaylistModel:
        """
        Crea un PlaylistModel con sus canciones asociadas.
        Nota: Este método debe usarse dentro de una transacción.
        """
        self.logger.debug(f"Creating playlist with songs for {entity.id}")

        # Crear la playlist
        playlist_model = self.entity_to_model(entity)
        playlist_model.save()

        # Crear las canciones asociadas si existen
        if entity.songs:
            playlist_songs = []
            for song_entity in entity.songs:
                playlist_song = PlaylistSongModel(
                    playlist=playlist_model,
                    song_id=song_entity.song_id,
                    position=song_entity.position,
                    added_at=song_entity.added_at,
                )
                playlist_songs.append(playlist_song)

            # Bulk create para mejor performance
            PlaylistSongModel.objects.bulk_create(playlist_songs)

        return playlist_model

    def update_playlist_songs(
        self, playlist_model: PlaylistModel, entity: PlaylistEntity
    ) -> None:
        """
        Actualiza las canciones de una playlist.
        Nota: Este método debe usarse dentro de una transacción.
        """
        self.logger.debug(f"Updating songs for playlist {entity.id}")

        if entity.songs is None:
            return

        # Eliminar todas las canciones existentes
        playlist_model.playlist_songs.all().delete()

        # Crear las nuevas canciones
        if entity.songs:
            playlist_songs = []
            for song_entity in entity.songs:
                playlist_song = PlaylistSongModel(
                    playlist=playlist_model,
                    song_id=song_entity.song_id,
                    position=song_entity.position,
                    added_at=song_entity.added_at,
                )
                playlist_songs.append(playlist_song)

            # Bulk create para mejor performance
            PlaylistSongModel.objects.bulk_create(playlist_songs)
