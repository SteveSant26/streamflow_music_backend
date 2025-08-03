from abc import ABC, abstractmethod
from typing import Optional


class IMediaDownloadService(ABC):
    """Interface para servicios de descarga de medios"""

    @abstractmethod
    async def download_thumbnail(self, url: str) -> Optional[bytes]:
        """
        Descarga una imagen thumbnail desde una URL

        Args:
            url: URL de la imagen

        Returns:
            Bytes de la imagen o None si falla
        """

    @abstractmethod
    async def download_audio(self, video_id: str) -> Optional[bytes]:
        """
        Descarga audio desde un video ID

        Args:
            video_id: ID del video

        Returns:
            Bytes del audio o None si falla
        """
