from typing import List, cast

from django.db.models import Q

from apps.music_catalog.domain.entities import SongEntity
from apps.music_catalog.domain.repository.Isong_repository import ISongRepository
from src.common.core import BaseDjangoRepository

from ..models import SongModel


class SongRepository(BaseDjangoRepository[SongEntity, SongModel], ISongRepository):
    """
    Implementación del repositorio de canciones que combina funcionalidades
    de solo lectura y solo escritura.
    """

    def __init__(self):
        super().__init__(SongModel)

    # Métodos específicos del repositorio de canciones (implementación de ISongRepository)

    def get_by_artist(self, artist_id: str) -> List[SongEntity]:
        songs = (
            SongModel.objects.select_related("artist", "album", "genre")
            .filter(artist_id=artist_id, is_active=True)
            .order_by("album__release_date", "track_number", "title")
        )
        return [self._model_to_entity(song) for song in songs]

    def get_by_album(self, album_id: str) -> List[SongEntity]:
        songs = (
            SongModel.objects.select_related("artist", "album", "genre")
            .filter(album_id=album_id, is_active=True)
            .order_by("track_number", "title")
        )
        return [self._model_to_entity(song) for song in songs]

    def get_by_genre(self, genre_id: str) -> List[SongEntity]:
        songs = (
            SongModel.objects.select_related("artist", "album", "genre")
            .filter(genre_id=genre_id, is_active=True)
            .order_by("-play_count", "title")
        )
        return [self._model_to_entity(song) for song in songs]

    def search_by_title(self, title: str) -> List[SongEntity]:
        songs = (
            SongModel.objects.select_related("artist", "album", "genre")
            .filter(Q(title__icontains=title) & Q(is_active=True))
            .order_by("-play_count", "title")[:50]
        )
        return [self._model_to_entity(song) for song in songs]

    def get_popular_songs(self, limit: int = 50) -> List[SongEntity]:
        songs = (
            SongModel.objects.select_related("artist", "album", "genre")
            .filter(is_active=True)
            .order_by("-play_count", "title")[:limit]
        )
        return [self._model_to_entity(song) for song in songs]

    def increment_play_count(self, song_id: str) -> bool:
        try:
            song = SongModel.objects.get(id=song_id, is_active=True)
            song.increment_play_count()
            return True
        except SongModel.DoesNotExist:
            return False

    # Implementación de métodos abstractos del repositorio base

    def _model_to_entity(self, model: SongModel) -> SongEntity:
        """Convierte un modelo Song a entidad SongEntity"""
        song_model = cast(SongModel, model)
        return SongEntity(
            id=str(song_model.id),
            title=song_model.title,
            artist_id=str(song_model.artist.id),
            artist_name=song_model.artist.name,
            album_id=str(song_model.album.id) if song_model.album else None,
            album_title=song_model.album.title if song_model.album else None,
            duration_seconds=song_model.duration_seconds,
            file_url=song_model.file_url,
            lyrics=song_model.lyrics,
            track_number=song_model.track_number,
            genre_id=str(song_model.genre.id) if song_model.genre else None,
            genre_name=song_model.genre.name if song_model.genre else None,
            play_count=song_model.play_count,
            is_active=song_model.is_active,
            created_at=song_model.created_at,
            updated_at=song_model.updated_at,
        )

    def _entity_to_model_data(self, entity: SongEntity) -> dict:
        data = {
            "title": entity.title,
            "artist_id": entity.artist_id,
            "duration_seconds": entity.duration_seconds,
            "file_url": entity.file_url,
            "lyrics": entity.lyrics,
            "track_number": entity.track_number,
            "play_count": entity.play_count,
            "is_active": entity.is_active,
        }
        if entity.album_id:
            data["album_id"] = entity.album_id
        if entity.genre_id:
            data["genre_id"] = entity.genre_id
        return data

    def _entity_to_model(self, entity: SongEntity) -> SongModel:
        """Convierte una entidad SongEntity a un modelo Django Song"""
        try:
            # Crea una nueva instancia del modelo Song con los datos de la entidad
            song_data = {
                "title": entity.title,
                "artist_id": entity.artist_id,
                "duration_seconds": entity.duration_seconds,
                "file_url": entity.file_url,
                "lyrics": entity.lyrics,
                "track_number": entity.track_number,
                "play_count": entity.play_count,
                "is_active": entity.is_active,
            }

            if entity.album_id:
                song_data["album_id"] = entity.album_id
            if entity.genre_id:
                song_data["genre_id"] = entity.genre_id

            # Si la entidad tiene un id (canción existente), incluirlo
            if hasattr(entity, "id") and entity.id is not None:
                song_data["id"] = entity.id

            song = SongModel(**song_data)
            return song

        except Exception as e:
            self.logger.error(f"Error al convertir entidad canción a modelo: {str(e)}")
            raise
