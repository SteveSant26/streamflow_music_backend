from abc import ABC, abstractmethod
from typing import Optional, Tuple


class IMediaFileService(ABC):
    """Interface para servicios de manejo de archivos multimedia"""

    @abstractmethod
    def generate_audio_filename(self, video_id: str) -> str:
        """Genera un nombre único para archivo de audio"""

    @abstractmethod
    def generate_thumbnail_filename(self, video_id: str, image_bytes: bytes) -> str:
        """Genera un nombre único para archivo de thumbnail"""

    @abstractmethod
    def get_image_extension(self, image_bytes: bytes) -> str:
        """Determina la extensión de archivo basada en los bytes de la imagen"""

    @abstractmethod
    def upload_media_files(
        self,
        audio_bytes: Optional[bytes],
        thumbnail_bytes: Optional[bytes],
        video_id: str,
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Sube archivos de audio y thumbnail al storage

        Returns:
            Tuple[audio_file_name, thumbnail_file_name, thumbnail_url]
        """
