from typing import Optional

import aiohttp

from common.interfaces.imedia_download_service import IMediaDownloadService
from common.utils.logging_config import get_logger
from common.utils.logging_decorators import log_execution


class MediaDownloadService(IMediaDownloadService):
    """Servicio para descarga de medios desde URLs"""

    def __init__(self, music_service=None):
        self.logger = get_logger(__name__)
        self.music_service = music_service

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    async def download_thumbnail(self, url: str) -> Optional[bytes]:
        """
        Descarga una imagen thumbnail desde una URL

        Args:
            url: URL de la imagen

        Returns:
            Bytes de la imagen o None si falla
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        self.logger.warning(
                            f"Failed to download thumbnail: HTTP {response.status}"
                        )
                        return None
        except Exception as e:
            self.logger.error(f"Error downloading thumbnail from {url}: {str(e)}")
            return None

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    async def download_audio(self, video_id: str) -> Optional[bytes]:
        """
        Descarga audio desde un video ID

        Args:
            video_id: ID del video

        Returns:
            Bytes del audio o None si falla
        """
        try:
            if not self.music_service:
                self.logger.error("Music service not available for audio download")
                return None

            return await self.music_service.download_audio_from_video(video_id)
        except Exception as e:
            self.logger.error(f"Error downloading audio for video {video_id}: {str(e)}")
            return None
