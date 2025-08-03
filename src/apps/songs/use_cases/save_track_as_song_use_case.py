from typing import Optional

from common.factories.media_service_factory import MediaServiceFactory
from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ...music_search.domain.interfaces import MusicTrackData
from ..domain.entities import SongEntity
from ..domain.repository import ISongRepository
from ..infrastructure.mappers.track_to_song_entity_mapper import TrackToSongEntityMapper


class SaveTrackAsSongUseCase(BaseUseCase[MusicTrackData, Optional[SongEntity]]):
    """Caso de uso para guardar un track de música como canción"""

    def __init__(
        self,
        song_repository: ISongRepository,
    ):
        super().__init__()
        self.song_repository = song_repository

        download_service, file_service = MediaServiceFactory.create_media_services()
        self.media_download_service = download_service
        self.media_file_service = file_service

        self.mapper = TrackToSongEntityMapper()

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(
        threshold_seconds=4.0
    )  # Operación de guardado y procesamiento de archivos
    async def execute(self, track: MusicTrackData) -> Optional[SongEntity]:
        """
        Convierte un MusicTrackData en SongEntity y lo guarda

        Args:
            track: Datos del track de música

        Returns:
            Entidad de canción guardada o None si falla
        """
        try:
            # Descargar medios (audio y thumbnail)
            audio_bytes, thumbnail_bytes = await self._download_media(track)

            # Subir archivos al storage
            (
                audio_file_name,
                thumbnail_file_name,
                updated_thumbnail_url,
            ) = await self.media_file_service.upload_media_files(
                audio_bytes, thumbnail_bytes, track.video_id
            )

            # Obtener URL del archivo de audio
            file_url = await self._get_audio_file_url(audio_file_name)

            # Crear entidad de canción usando el mapper
            song_entity = self.mapper.map(
                track, file_url=file_url, thumbnail_url=updated_thumbnail_url
            )

            self.logger.info(f"Saving track as song: {track.title}")
            return await self.song_repository.save(song_entity)

        except Exception as e:
            self.logger.error(f"Error saving track as song: {str(e)}")
            return None

    async def _download_media(
        self, track: MusicTrackData
    ) -> tuple[Optional[bytes], Optional[bytes]]:
        """
        Descarga audio y thumbnail del track

        Args:
            track: Datos del track

        Returns:
            Tuple[audio_bytes, thumbnail_bytes]
        """
        audio_bytes = None
        thumbnail_bytes = None

        # Descargar audio si no existe y hay video_id
        if not track.audio_file_name and track.video_id:
            self.logger.info(f"Downloading audio for track: {track.title}")
            audio_bytes = await self.media_download_service.download_audio(
                track.video_id
            )
            if not audio_bytes:
                self.logger.warning(
                    f"Failed to download audio for track: {track.title}"
                )

        # Descargar thumbnail si existe URL
        if track.thumbnail_url:
            self.logger.info(f"Downloading thumbnail for track: {track.title}")
            thumbnail_bytes = await self.media_download_service.download_thumbnail(
                track.thumbnail_url
            )
            if not thumbnail_bytes:
                self.logger.warning(
                    f"Failed to download thumbnail for track: {track.title}"
                )

        return audio_bytes, thumbnail_bytes

    async def _get_audio_file_url(
        self, audio_file_name: Optional[str]
    ) -> Optional[str]:
        """
        Obtiene la URL del archivo de audio si existe

        Args:
            audio_file_name: Nombre del archivo de audio

        Returns:
            URL del archivo o None
        """
        if audio_file_name:
            # Acceder al storage a través del factory para obtener la URL
            from common.factories import StorageServiceFactory

            storage_service = StorageServiceFactory.create_music_files_service()
            return storage_service.get_item_url(audio_file_name)
        return None
