from typing import Optional

from common.factories import StorageServiceFactory
from common.factories.unified_music_service_factory import get_music_service
from common.interfaces.imedia_download_service import IMediaDownloadService
from common.interfaces.imedia_file_service import IMediaFileService
from common.interfaces.istorage_service import IStorageService

from ..adapters.media.media_download_service import MediaDownloadService
from ..adapters.media.media_file_service import MediaFileService


class MediaServiceFactory:
    """Factory para crear servicios relacionados con medios"""

    @staticmethod
    def create_media_download_service(music_service=None) -> IMediaDownloadService:
        """Crea un servicio de descarga de medios"""
        if music_service is None:
            music_service = get_music_service()
        return MediaDownloadService(music_service)

    @staticmethod
    def create_media_file_service(
        storage_service: Optional[IStorageService] = None,
    ) -> IMediaFileService:
        """Crea un servicio de manejo de archivos multimedia"""
        if storage_service is None:
            storage_service = StorageServiceFactory.create_music_files_service()
        return MediaFileService(storage_service)

    @staticmethod
    def create_media_services() -> tuple[IMediaDownloadService, IMediaFileService]:
        """Crea todos los servicios de medios necesarios"""
        download_service = MediaServiceFactory.create_media_download_service()
        file_service = MediaServiceFactory.create_media_file_service()
        return download_service, file_service
