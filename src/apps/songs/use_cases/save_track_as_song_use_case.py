import uuid
from datetime import datetime
from typing import Optional

from common.factories import StorageServiceFactory
from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ...music_search.domain.interfaces import MusicTrackData
from ..domain.entities import SongEntity
from ..domain.repository.Isong_repository import ISongRepository


class SaveTrackAsSongUseCase(BaseUseCase[MusicTrackData, Optional[SongEntity]]):
    """Caso de uso para guardar un track de música como canción"""

    def __init__(self, song_repository: ISongRepository):
        super().__init__()
        self.song_repository = song_repository
        self.music_storage = StorageServiceFactory.create_music_files_service()

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    async def execute(self, track: MusicTrackData) -> Optional[SongEntity]:
        """
        Convierte un MusicTrackData en SongEntity y lo guarda

        Args:
            track: Datos del track de música

        Returns:
            Entidad de canción guardada o None si falla
        """
        try:
            # Obtener URL del archivo de audio si existe
            file_url = None
            if track.audio_file_name:
                file_url = self.music_storage.get_item_url(track.audio_file_name)

            song_entity = SongEntity(
                id=str(uuid.uuid4()),
                title=track.title,
                artist_name=track.artist_name,
                album_title=track.album_title,
                duration_seconds=track.duration_seconds,
                file_url=file_url,
                thumbnail_url=track.thumbnail_url,
                genre_name=track.genre,
                tags=track.tags,
                source_type="youtube",
                source_id=track.video_id,
                source_url=track.url,
                is_active=True,
                audio_quality="standard",
                created_at=datetime.now(),
                release_date=datetime.now(),
            )

            self.logger.info(f"Saving track as song: {track.title}")
            return await self.song_repository.save(song_entity)

        except Exception as e:
            self.logger.error(f"Error saving track as song: {str(e)}")
            return None
