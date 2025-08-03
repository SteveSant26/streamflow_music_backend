import io
import uuid
from typing import Optional, Tuple

from common.interfaces.imedia_file_service import IMediaFileService
from common.interfaces.istorage_service import IStorageService
from common.utils.logging_decorators import log_execution
from src.common.mixins.logging_mixin import LoggingMixin


class MediaFileService(IMediaFileService, LoggingMixin):
    """Servicio para manejo de archivos multimedia"""

    def __init__(self, storage_service: IStorageService):
        super().__init__()
        self.storage_service = storage_service

    def generate_audio_filename(self, video_id: str) -> str:
        """Genera un nombre único para archivo de audio"""
        return f"audio/{video_id}_{uuid.uuid4().hex[:8]}.mp3"

    def generate_thumbnail_filename(self, video_id: str, image_bytes: bytes) -> str:
        """Genera un nombre único para archivo de thumbnail"""
        file_extension = self.get_image_extension(image_bytes)
        return f"thumbnails/{video_id}_{uuid.uuid4().hex[:8]}.{file_extension}"

    def get_image_extension(self, image_bytes: bytes) -> str:
        """
        Determina la extensión de archivo basada en los bytes de la imagen

        Args:
            image_bytes: Bytes de la imagen

        Returns:
            Extensión del archivo (jpg, png, webp, etc.)
        """
        # Verificar los primeros bytes para determinar el formato
        if image_bytes.startswith(b"\xff\xd8\xff"):
            return "jpg"
        elif image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return "png"
        elif image_bytes.startswith(b"RIFF") and b"WEBP" in image_bytes[:12]:
            return "webp"
        elif image_bytes.startswith(b"GIF87a") or image_bytes.startswith(b"GIF89a"):
            return "gif"
        else:
            # Por defecto, usar jpg
            return "jpg"

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    async def upload_media_files(
        self,
        audio_bytes: Optional[bytes],
        thumbnail_bytes: Optional[bytes],
        video_id: str,
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Sube archivos de audio y thumbnail al storage

        Args:
            audio_bytes: Bytes del archivo de audio
            thumbnail_bytes: Bytes del thumbnail
            video_id: ID del video

        Returns:
            Tuple[audio_file_name, thumbnail_file_name, thumbnail_url]
        """
        audio_file_name = None
        thumbnail_file_name = None
        thumbnail_url = None

        # Subir archivo de audio
        if audio_bytes:
            audio_file_name = await self._upload_audio_file(audio_bytes, video_id)

        # Subir thumbnail
        if thumbnail_bytes:
            thumbnail_file_name, thumbnail_url = await self._upload_thumbnail_file(
                thumbnail_bytes, video_id
            )

        return audio_file_name, thumbnail_file_name, thumbnail_url

    async def _upload_audio_file(
        self, audio_bytes: bytes, video_id: str
    ) -> Optional[str]:
        """Sube archivo de audio al storage"""
        try:
            audio_file_name = self.generate_audio_filename(video_id)
            audio_file_obj = io.BytesIO(audio_bytes)

            upload_success = self.storage_service.upload_item(
                audio_file_name, audio_file_obj
            )

            if upload_success:
                self.logger.info(f"Audio uploaded successfully: {audio_file_name}")
                return audio_file_name
            else:
                self.logger.error(f"Failed to upload audio for video: {video_id}")
                return None

        except Exception as e:
            self.logger.error(f"Error uploading audio for video {video_id}: {str(e)}")
            return None

    async def _upload_thumbnail_file(
        self, thumbnail_bytes: bytes, video_id: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Sube thumbnail al storage"""
        try:
            thumbnail_file_name = self.generate_thumbnail_filename(
                video_id, thumbnail_bytes
            )
            thumbnail_file_obj = io.BytesIO(thumbnail_bytes)

            upload_success = self.storage_service.upload_item(
                thumbnail_file_name, thumbnail_file_obj
            )

            if upload_success:
                self.logger.info(
                    f"Thumbnail uploaded successfully: {thumbnail_file_name}"
                )
                thumbnail_url = self.storage_service.get_item_url(thumbnail_file_name)
                return thumbnail_file_name, thumbnail_url
            else:
                self.logger.error(f"Failed to upload thumbnail for video: {video_id}")
                return None, None

        except Exception as e:
            self.logger.error(
                f"Error uploading thumbnail for video {video_id}: {str(e)}"
            )
            return None, None
