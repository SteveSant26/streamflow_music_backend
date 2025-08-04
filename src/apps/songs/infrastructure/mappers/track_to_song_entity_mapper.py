import uuid
from typing import List, Optional

from django.utils import timezone

from common.mixins.logging_mixin import LoggingMixin

from ....genres.infrastructure.repository.genre_repository import GenreRepository
from ....music_search.domain.interfaces import MusicTrackData
from ...domain.entities import SongEntity


class TrackToSongEntityMapper(LoggingMixin):
    """Mapper para convertir MusicTrackData a SongEntity"""

    def __init__(self):
        super().__init__()
        self.genre_repository = GenreRepository()

    async def map(
        self,
        track: MusicTrackData,
        file_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        analyzed_genres: Optional[List[str]] = None,
        artist_id: Optional[str] = None,
        album_id: Optional[str] = None,
    ) -> SongEntity:
        """
        Convierte un MusicTrackData en SongEntity

        Args:
            track: Datos del track de música
            file_url: URL del archivo de audio (opcional)
            thumbnail_url: URL del thumbnail (opcional, usa el del track si no se proporciona)
            analyzed_genres: Lista de nombres de géneros analizados automáticamente (opcional)
            artist_id: ID del artista (opcional)
            album_id: ID del álbum (opcional)

        Returns:
            Entidad de canción
        """
        # Convertir nombres de géneros a IDs de géneros
        genre_ids = []
        if analyzed_genres:
            try:
                genre_ids = await self._get_genre_ids_from_names(analyzed_genres)
            except Exception as e:
                # Si hay error obteniendo los IDs, continuar sin géneros
                self.logger.error(f"Error obteniendo IDs de géneros: {str(e)}")
                genre_ids = []

        return SongEntity(
            id=str(uuid.uuid4()),
            title=track.title,
            artist_id=artist_id,  # Usar el artist_id proporcionado
            album_id=album_id,  # Usar el album_id proporcionado
            album_title=track.album_title,
            duration_seconds=track.duration_seconds,
            file_url=file_url,
            thumbnail_url=thumbnail_url or track.thumbnail_url,
            source_type="youtube",
            source_id=track.video_id,
            source_url=track.url,
            audio_quality="standard",
            created_at=timezone.now(),
            release_date=timezone.now(),
            genre_ids=genre_ids,  # Asignar los IDs de géneros obtenidos
        )

    async def _get_genre_ids_from_names(self, genre_names: List[str]) -> List[str]:
        """
        Convierte una lista de nombres de géneros a una lista de IDs de géneros

        Args:
            genre_names: Lista de nombres de géneros

        Returns:
            Lista de IDs de géneros (como strings)
        """
        from asgiref.sync import sync_to_async

        from ....genres.infrastructure.models import GenreModel

        genre_ids = []

        for genre_name in genre_names:
            try:
                # Buscar el género por nombre (case insensitive) directamente en el modelo
                genre_model = await sync_to_async(
                    lambda name=genre_name: GenreModel.objects.filter(
                        name__iexact=name
                    ).first()
                )()

                if genre_model:
                    genre_ids.append(str(genre_model.id))
            except Exception as e:
                # Si hay error con un género específico, continuar con los demás
                self.logger.error(f"Error buscando género '{genre_name}': {str(e)}")
                continue

        return genre_ids
