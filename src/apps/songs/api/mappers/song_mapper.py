from apps.songs.domain.entities import SongEntity
from apps.songs.infrastructure.models.song_model import SongModel
from common.interfaces.imapper.abstract_mapper import AbstractMapper
from common.mixins.logging_mixin import LoggingMixin

from ..dtos import SongResponseDTO


class SongMapper(AbstractMapper, LoggingMixin):
    """Mapper para convertir entre entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: SongModel) -> SongEntity:
        """
        Convierte un modelo de Django a entidad del dominio.
        """
        self.logger.debug(f"Converting model to entity for song {model.id}")
        return SongEntity(
            id=str(model.id),
            title=model.title,
            album_id=str(model.album_id) if model.album_id else None,
            artist_id=str(model.artist_id) if model.artist_id else None,
            genre_id=str(model.genre_id) if model.genre_id else None,
            duration_seconds=model.duration_seconds,
            album_title=model.album_title,
            artist_name=model.artist_name,
            genre_name=model.genre_name,
            track_number=model.track_number,
            file_url=model.file_url,
            thumbnail_url=model.thumbnail_url,
            lyrics=model.lyrics,
            tags=model.tags,
            play_count=model.play_count,
            favorite_count=model.favorite_count,
            download_count=model.download_count,
            source_type=model.source_type,
            source_id=model.source_id,
            source_url=model.source_url,
            is_active=model.is_active,
            audio_quality=model.audio_quality,
            created_at=model.created_at,
            release_date=model.release_date,
        )

    def entity_to_response_dto(self, entity: SongEntity) -> SongResponseDTO:
        """
        Convierte una entidad del dominio a DTO de respuesta.
        """
        self.logger.debug(f"Converting entity to DTO for song {entity.id}")

        return SongResponseDTO(
            id=entity.id,
            title=entity.title,
            album_id=entity.album_id,
            artist_id=entity.artist_id,
            genre_id=entity.genre_id,
            duration_seconds=entity.duration_seconds,
            album_title=entity.album_title,
            artist_name=entity.artist_name,
            genre_name=entity.genre_name,
            track_number=entity.track_number,
            file_url=entity.file_url,
            thumbnail_url=entity.thumbnail_url,
            lyrics=entity.lyrics,
            tags=entity.tags,
            play_count=entity.play_count,
            favorite_count=entity.favorite_count,
            download_count=entity.download_count,
            source_type=entity.source_type,
            source_id=entity.source_id,
            source_url=entity.source_url,
            is_active=entity.is_active,
            audio_quality=entity.audio_quality,
            created_at=entity.created_at,
            release_date=entity.release_date,
            audio_downloaded=bool(entity.file_url),  # True si hay URL de archivo
            # Campos adicionales mapeados desde los campos existentes
            youtube_video_id=entity.source_id
            if entity.source_type == "youtube"
            else None,
            youtube_url=entity.source_url if entity.source_type == "youtube" else None,
            youtube_view_count=0,  # Este podríamos poblarlo desde metadata si está disponible
            youtube_like_count=0,  # Este podríamos poblarlo desde metadata si está disponible
            is_explicit=False,  # Por defecto False, se podría determinar desde tags o metadata
            published_at=entity.release_date,  # Usamos release_date como published_at
        )

    def dto_to_entity(self, dto: SongResponseDTO) -> SongEntity:
        """
        Convierte un DTO a entidad del dominio.
        """
        return SongEntity(
            id=dto.id,
            title=dto.title,
            album_id=dto.album_id,
            artist_id=dto.artist_id,
            genre_id=dto.genre_id,
            duration_seconds=dto.duration_seconds,
            album_title=dto.album_title,
            artist_name=dto.artist_name,
            genre_name=dto.genre_name,
            track_number=dto.track_number,
            file_url=dto.file_url,
            thumbnail_url=dto.thumbnail_url,
            lyrics=dto.lyrics,
            tags=dto.tags,
            play_count=dto.play_count,
            favorite_count=dto.favorite_count,
            download_count=dto.download_count,
            source_type=dto.source_type or "youtube",
            source_id=dto.source_id,
            source_url=dto.source_url,
            is_active=dto.is_active,
            audio_quality=dto.audio_quality or "standard",
            created_at=dto.created_at,
            release_date=dto.release_date,
            # Nota: audio_downloaded se calcula a partir de file_url, no se almacena en la entidad
        )
