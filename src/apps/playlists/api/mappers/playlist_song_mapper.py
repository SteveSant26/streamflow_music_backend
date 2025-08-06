from typing import List, Optional

from apps.playlists.domain.entities import PlaylistSongEntity
from apps.playlists.infrastructure.models import PlaylistSongModel
from common.interfaces.imapper.abstract_mapper import AbstractMapper


class PlaylistSongMapper(AbstractMapper):
    """Mapper completo para canciones en playlist que combina model-entity y entity-dto"""

    def __init__(self):
        super().__init__()
        # Lazy initialization to avoid circular imports
        self._model_mapper = None
        self._dto_mapper = None

    @property
    def model_mapper(self):
        if self._model_mapper is None:
            from .playlist_song_entity_model_mapper import PlaylistSongEntityModelMapper

            self._model_mapper = PlaylistSongEntityModelMapper()
        return self._model_mapper

    @property
    def dto_mapper(self):
        if self._dto_mapper is None:
            from .playlist_song_entity_dto_mapper import PlaylistSongEntityDTOMapper

            self._dto_mapper = PlaylistSongEntityDTOMapper()
        return self._dto_mapper

    # Delegate methods to maintain the same interface
    def model_to_entity(self, model: PlaylistSongModel) -> PlaylistSongEntity:
        """Delegate to model mapper"""
        return self.model_mapper.model_to_entity(model)

    def entity_to_dto(self, entity: PlaylistSongEntity):
        """Delegate to DTO mapper"""
        return self.dto_mapper.entity_to_dto(entity)

    def dto_to_entity(self, dto):
        """Delegate to DTO mapper"""
        return self.dto_mapper.dto_to_entity(dto)

    def get_playlist_songs(
        self, playlist_id: str, with_song_info: bool = True
    ) -> List[PlaylistSongEntity]:
        """
        Obtiene todas las canciones de una playlist

        Args:
            playlist_id: ID de la playlist
            with_song_info: Si incluir información de las canciones

        Returns:
            Lista de PlaylistSongEntity ordenadas por posición
        """
        try:
            queryset = PlaylistSongModel.objects.filter(playlist_id=playlist_id)

            if with_song_info:
                queryset = queryset.select_related("song__artist")

            playlist_songs = queryset.order_by("position")
            return self.model_mapper.models_to_entities(playlist_songs)

        except Exception as e:
            self.logger.error(
                f"Error getting songs for playlist {playlist_id}: {str(e)}"
            )
            return []

    def add_song_to_playlist(
        self, playlist_id: str, song_id: str, position: Optional[int] = None
    ) -> Optional[PlaylistSongEntity]:
        """
        Añade una canción a una playlist

        Args:
            playlist_id: ID de la playlist
            song_id: ID de la canción
            position: Posición específica (opcional, se añade al final si no se especifica)

        Returns:
            PlaylistSongEntity creada o None si hay error
        """
        try:
            from datetime import datetime

            from django.db import transaction

            with transaction.atomic():
                # Determinar la posición si no se especifica
                if position is None:
                    last_song = (
                        PlaylistSongModel.objects.filter(playlist_id=playlist_id)
                        .order_by("-position")
                        .first()
                    )
                    position = (last_song.position + 1) if last_song else 1
                else:
                    # Mover canciones existentes si es necesario
                    from django.db.models import F

                    PlaylistSongModel.objects.filter(
                        playlist_id=playlist_id, position__gte=position
                    ).update(position=F("position") + 1)

                # Crear la nueva entrada
                playlist_song = PlaylistSongModel.objects.create(
                    playlist_id=playlist_id,
                    song_id=song_id,
                    position=position,
                    added_at=datetime.now(),
                )

                return self.model_mapper.model_to_entity(playlist_song)

        except Exception as e:
            self.logger.error(f"Error adding song to playlist: {str(e)}")
            return None

    def remove_song_from_playlist(self, playlist_id: str, song_id: str) -> bool:
        """
        Remueve una canción de una playlist

        Args:
            playlist_id: ID de la playlist
            song_id: ID de la canción

        Returns:
            True si se removió correctamente, False en caso contrario
        """
        try:
            from django.db import transaction

            with transaction.atomic():
                # Encontrar y eliminar la canción
                playlist_song = PlaylistSongModel.objects.get(
                    playlist_id=playlist_id, song_id=song_id
                )
                removed_position = playlist_song.position
                playlist_song.delete()

                # Actualizar posiciones de canciones posteriores
                from django.db.models import F

                PlaylistSongModel.objects.filter(
                    playlist_id=playlist_id, position__gt=removed_position
                ).update(position=F("position") - 1)

                return True

        except PlaylistSongModel.DoesNotExist:
            self.logger.warning(f"Song {song_id} not found in playlist {playlist_id}")
            return False
        except Exception as e:
            self.logger.error(f"Error removing song from playlist: {str(e)}")
            return False

    def move_song_in_playlist(
        self, playlist_id: str, song_id: str, new_position: int
    ) -> bool:
        """
        Mueve una canción a una nueva posición en la playlist

        Args:
            playlist_id: ID de la playlist
            song_id: ID de la canción
            new_position: Nueva posición

        Returns:
            True si se movió correctamente, False en caso contrario
        """
        try:
            from django.db import transaction
            from django.db.models import F

            with transaction.atomic():
                # Encontrar la canción
                playlist_song = PlaylistSongModel.objects.get(
                    playlist_id=playlist_id, song_id=song_id
                )
                old_position = playlist_song.position

                if old_position == new_position:
                    return True  # No hay cambio

                # Actualizar posiciones según el movimiento
                if old_position < new_position:
                    # Mover hacia abajo: decrementar posiciones intermedias
                    PlaylistSongModel.objects.filter(
                        playlist_id=playlist_id,
                        position__gt=old_position,
                        position__lte=new_position,
                    ).update(position=F("position") - 1)
                else:
                    # Mover hacia arriba: incrementar posiciones intermedias
                    PlaylistSongModel.objects.filter(
                        playlist_id=playlist_id,
                        position__gte=new_position,
                        position__lt=old_position,
                    ).update(position=F("position") + 1)

                # Actualizar la posición de la canción movida
                playlist_song.position = new_position
                playlist_song.save()

                return True

        except PlaylistSongModel.DoesNotExist:
            self.logger.warning(f"Song {song_id} not found in playlist {playlist_id}")
            return False
        except Exception as e:
            self.logger.error(f"Error moving song in playlist: {str(e)}")
            return False
