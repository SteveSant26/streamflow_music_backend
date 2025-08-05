"""
Procesador para archivos multimedia
"""

import logging
from typing import Optional, Tuple

from common.factories import StorageServiceFactory
from common.factories.media_service_factory import MediaServiceFactory

from ....music_search.domain.interfaces import MusicTrackData
from ..validators.media_validators import MediaValidators


class MediaProcessor:
    """Procesador para descargar y subir archivos multimedia"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        download_service, file_service = MediaServiceFactory.create_media_services()
        self.media_download_service = download_service
        self.media_file_service = file_service
        self.validators = MediaValidators()

    async def download_media(
        self, track: MusicTrackData
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
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
            self.logger.info(f"🎵 Downloading audio for track: {track.title}")
            try:
                audio_bytes = await self.media_download_service.download_audio(
                    track.video_id
                )
                if not audio_bytes:
                    self.logger.error(
                        f"❌ Failed to download audio for track: {track.title} (video_id: {track.video_id})"
                    )
                else:
                    self.logger.info(
                        f"✅ Successfully downloaded audio for track: {track.title} ({len(audio_bytes)} bytes)"
                    )
            except Exception as e:
                self.logger.error(
                    f"❌ Exception during audio download for track: {track.title} - {str(e)}"
                )

        # Descargar thumbnail si existe URL
        if track.thumbnail_url:
            self.logger.info(f"🖼️ Downloading thumbnail for track: {track.title}")
            try:
                thumbnail_bytes = await self.media_download_service.download_thumbnail(
                    track.thumbnail_url
                )
                if not thumbnail_bytes:
                    self.logger.warning(
                        f"⚠️ Failed to download thumbnail for track: {track.title}"
                    )
                else:
                    self.logger.info(
                        f"✅ Successfully downloaded thumbnail for track: {track.title} ({len(thumbnail_bytes)} bytes)"
                    )
            except Exception as e:
                self.logger.warning(
                    f"⚠️ Exception during thumbnail download for track: {track.title} - {str(e)}"
                )

        return audio_bytes, thumbnail_bytes

    def get_audio_file_url(self, audio_file_name: Optional[str]) -> Optional[str]:
        """
        Obtiene la URL del archivo de audio si existe

        Args:
            audio_file_name: Nombre del archivo de audio

        Returns:
            URL del archivo o None
        """
        if audio_file_name:
            storage_service = StorageServiceFactory.create_music_files_service()
            return storage_service.get_item_url(audio_file_name)
        return None

    async def process_media_files(
        self, music_track: MusicTrackData
    ) -> Optional[Tuple[Optional[str], Optional[str]]]:
        """
        Procesa descarga y subida de archivos multimedia

        Args:
            music_track: Datos del track de música

        Returns:
            Tuple[file_url, updated_thumbnail_url] o None si falla
        """
        # Descargar medios
        audio_bytes, thumbnail_bytes = await self.download_media(music_track)

        # Validar descarga de audio
        if not self.validators.validate_audio_download(music_track, audio_bytes):
            return None

        # Subir archivos al storage
        (
            audio_file_name,
            _,
            updated_thumbnail_url,
        ) = await self.media_file_service.upload_media_files(
            audio_bytes, thumbnail_bytes, music_track.video_id
        )

        # Validar subida al storage
        if not self.validators.validate_storage_upload(
            music_track, audio_bytes, audio_file_name
        ):
            return None

        # Obtener URL del archivo
        file_url = self.get_audio_file_url(audio_file_name)

        # Validar URL del archivo
        if not self.validators.validate_file_url(music_track, audio_bytes, file_url):
            return None

        self.logger.info(
            f"✅ Audio file successfully uploaded to storage for track: {music_track.title}. "
            f"Proceeding to save in database."
        )

        return file_url, updated_thumbnail_url
