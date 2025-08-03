import uuid
from typing import Optional

from django.utils import timezone

from ....music_search.domain.interfaces import MusicTrackData
from ...domain.entities import SongEntity


class TrackToSongEntityMapper:
    """Mapper para convertir MusicTrackData a SongEntity"""

    def map(
        self,
        track: MusicTrackData,
        file_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
    ) -> SongEntity:
        """
        Convierte un MusicTrackData en SongEntity

        Args:
            track: Datos del track de música
            file_url: URL del archivo de audio (opcional)
            thumbnail_url: URL del thumbnail (opcional, usa el del track si no se proporciona)

        Returns:
            Entidad de canción
        """
        return SongEntity(
            id=str(uuid.uuid4()),
            title=track.title,
            artist_name=track.artist_name,
            album_title=track.album_title,
            duration_seconds=track.duration_seconds,
            file_url=file_url,
            thumbnail_url=thumbnail_url or track.thumbnail_url,
            genre_names=[track.genre] if track.genre else [],
            source_type="youtube",
            source_id=track.video_id,
            source_url=track.url,
            audio_quality="standard",
            created_at=timezone.now(),
            release_date=timezone.now(),
        )
