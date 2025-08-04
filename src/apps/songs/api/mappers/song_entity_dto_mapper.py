from typing import List

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
        Obtiene nombres de géneros usando los IDs.
        """
        self.logger.debug(f"Converting entity to DTO for song {entity.id}")

        # Obtener nombres de géneros basándose en genre_ids (síncronamente)
        genre_names = self._get_genre_names_from_ids_sync(entity.genre_ids or [])

        # Por ahora artist_name será None hasta que se implemente artists
        artist_name = None

        return SongResponseDTO(
            id=entity.id,
            title=entity.title,
            album_id=entity.album_id,
            artist_id=entity.artist_id,
            genre_ids=entity.genre_ids,
            duration_seconds=entity.duration_seconds,
            album_title=entity.album_title,
            artist_name=artist_name,
            genre_names=genre_names,
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
            audio_downloaded=bool(entity.file_url),
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
        )

    def _get_genre_names_from_ids_sync(self, genre_ids: List[str]) -> List[str]:
        """
        Obtiene nombres de géneros a partir de sus IDs (versión síncrona)

        Args:
            genre_ids: Lista de IDs de géneros

        Returns:
            Lista de nombres de géneros
        """
        if not genre_ids:
            return []

        try:
            from apps.genres.infrastructure.models import GenreModel

            # Buscar los géneros por IDs de forma síncrona
            genre_names = list(
                GenreModel.objects.filter(id__in=genre_ids).values_list(
                    "name", flat=True
                )
            )

            return genre_names

        except Exception as e:
            self.logger.error(f"Error obteniendo nombres de géneros: {str(e)}")
            return []
