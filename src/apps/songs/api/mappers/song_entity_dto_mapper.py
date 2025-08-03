from apps.songs.domain.entities import SongEntity
from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper
from common.mixins.logging_mixin import LoggingMixin

from ..dtos import SongResponseDTO


class SongEntityDTOMapper(
    AbstractEntityDtoMapper[SongEntity, SongResponseDTO], LoggingMixin
):
    """Mapper para convertir entre entidades del dominio y DTOs de la API."""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: SongEntity) -> SongResponseDTO:
        """
        Convierte una entidad del dominio a DTO de respuesta.
        """
        self.logger.debug(f"Converting entity to DTO for song {entity.id}")

        return SongResponseDTO(
            id=entity.id,
            title=entity.title,
            album_id=entity.album_id,
            artist_id=entity.artist_id,
            genre_ids=entity.genre_ids,
            duration_seconds=entity.duration_seconds,
            album_title=entity.album_title,
            artist_name=entity.artist_name,
            genre_names=entity.genre_names,
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
            created_at=entity.created_at,
            release_date=entity.release_date,
            audio_downloaded=bool(
                entity.file_url
            ),  # True si hay URL de archivo # Usamos release_date como published_at
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
            genre_ids=dto.genre_ids,
            duration_seconds=dto.duration_seconds,
            album_title=dto.album_title,
            artist_name=dto.artist_name,
            genre_names=dto.genre_names,
            track_number=dto.track_number,
            file_url=dto.file_url,
            thumbnail_url=dto.thumbnail_url,
            lyrics=dto.lyrics,
            play_count=dto.play_count,
            favorite_count=dto.favorite_count,
            download_count=dto.download_count,
            source_type=dto.source_type or "youtube",
            source_id=dto.source_id,
            source_url=dto.source_url,
            audio_quality=dto.audio_quality or "standard",
            created_at=dto.created_at,
            release_date=dto.release_date,
            # Nota: audio_downloaded se calcula a partir de file_url, no se almacena en la entidad
        )
