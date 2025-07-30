from common.adapters import SupabaseStorageAdapter
from common.interfaces import IStorageService


class StorageServiceFactory:
    """Factory para crear servicios de storage según la configuración."""

    @staticmethod
    def __create_storage_service(bucket_name: str) -> IStorageService:
        """
        Crea un servicio de storage.

        Args:
            bucket_name: Nombre del bucket/contenedor

        Returns:
            IStorageService: Implementación del servicio de storage
        """
        # Por ahora solo tenemos Supabase, pero aquí podrías agregar lógica
        # para elegir entre diferentes proveedores (AWS S3, Google Cloud, etc.)
        return SupabaseStorageAdapter(bucket_name)

    @staticmethod
    def create_profile_pictures_service() -> IStorageService:
        """Crea un servicio específico para fotos de perfil."""
        return StorageServiceFactory.__create_storage_service("profile-pictures")

    @staticmethod
    def create_music_files_service() -> IStorageService:
        """Crea un servicio específico para archivos de música."""
        return StorageServiceFactory.__create_storage_service("music-files")

    @staticmethod
    def create_album_covers_service() -> IStorageService:
        """Crea un servicio específico para portadas de álbumes."""
        return StorageServiceFactory.__create_storage_service("album-covers")
