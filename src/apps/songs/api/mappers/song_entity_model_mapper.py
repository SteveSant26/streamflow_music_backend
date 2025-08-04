from typing import Any, Dict, List

from apps.songs.domain.entities import SongEntity
from apps.songs.infrastructure.models import SongModel
from common.interfaces.imapper import AbstractEntityModelMapper


class SongEntityModelMapper(AbstractEntityModelMapper[SongEntity, SongModel]):
    """Mapper para convertir entre entidades del dominio y modelos de Song."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: SongModel) -> SongEntity:
        """
        Convierte un modelo Django SongModel a entidad del dominio SongEntity.
        """
        self.logger.debug(f"Converting model to entity for song {model.id}")

        genre_ids = []
        if hasattr(model, "genres"):
            try:
                genre_ids = [str(genre.id) for genre in model.genres.all()]
            except Exception:
                genre_ids = []

        return SongEntity(
            id=str(model.id),
            title=model.title,
            album_id=str(model.album_id) if model.album_id else None,
            artist_id=str(model.artist_id) if model.artist_id else None,
            genre_ids=genre_ids,
            duration_seconds=model.duration_seconds,
            album_title=model.album_title,
            artist_name=getattr(model, "artist_name", None),  # Backwards compatible
            track_number=model.track_number,
            file_url=model.file_url,
            thumbnail_url=model.thumbnail_url,
            lyrics=model.lyrics,
            play_count=model.play_count,
            favorite_count=model.favorite_count,
            download_count=model.download_count,
            source_type=model.source_type,
            source_id=model.source_id,
            source_url=model.source_url,
            audio_quality=model.audio_quality,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_played_at=model.last_played_at,
            release_date=model.release_date,
        )

    def entity_to_model(self, entity: SongEntity) -> SongModel:
        """
        Convierte una entidad SongEntity a una instancia del modelo Django SongModel.
        """
        self.logger.debug(f"Converting entity to model instance for song {entity.id}")

        model_instance = SongModel(
            id=entity.id if hasattr(entity, "id") and entity.id is not None else None,
            title=entity.title,
            album_id=entity.album_id,
            artist_id=entity.artist_id,
            duration_seconds=entity.duration_seconds,
            album_title=entity.album_title,
            track_number=entity.track_number,
            file_url=entity.file_url,
            thumbnail_url=entity.thumbnail_url,
            lyrics=entity.lyrics,
            play_count=entity.play_count,
            favorite_count=entity.favorite_count,
            download_count=entity.download_count,
            source_type=entity.source_type,
            source_id=entity.source_id,
            source_url=entity.source_url,
            audio_quality=entity.audio_quality,
            last_played_at=getattr(entity, "last_played_at", None),
            release_date=entity.release_date,
        )

        return model_instance

    def entity_to_model_data(self, entity: SongEntity) -> Dict[str, Any]:
        """
        Convierte una entidad SongEntity a datos del modelo Django (diccionario).
        """
        self.logger.debug(f"Converting entity to model data for song {entity.id}")

        model_data = {
            "title": entity.title,
            "album_id": entity.album_id,
            "artist_id": entity.artist_id,
            "duration_seconds": entity.duration_seconds,
            "album_title": entity.album_title,
            "track_number": entity.track_number,
            "file_url": entity.file_url,
            "thumbnail_url": entity.thumbnail_url,
            "lyrics": entity.lyrics,
            "play_count": entity.play_count,
            "favorite_count": entity.favorite_count,
            "download_count": entity.download_count,
            "source_type": entity.source_type,
            "source_id": entity.source_id,
            "source_url": entity.source_url,
            "audio_quality": entity.audio_quality,
            "last_played_at": getattr(entity, "last_played_at", None),
            "release_date": entity.release_date,
        }

        return model_data

    async def set_entity_genres_to_model(
        self, model: SongModel, genre_ids: List[str]
    ) -> None:
        """
        Asigna los géneros a un modelo de canción ya guardado.

        Args:
            model: Instancia del modelo SongModel ya guardada en la base de datos
            genre_ids: Lista de IDs de géneros a asignar
        """
        if genre_ids:
            # Necesitamos importar aquí para evitar imports circulares
            from asgiref.sync import sync_to_async

            from apps.genres.infrastructure.models import GenreModel

            genre_objects = await sync_to_async(list)(
                GenreModel.objects.filter(id__in=genre_ids)
            )
            await sync_to_async(model.genres.set)(genre_objects)
