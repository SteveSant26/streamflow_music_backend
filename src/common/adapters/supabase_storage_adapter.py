from ..interfaces.istorage_service import IStorageService
from ..mixins.logging_mixin import LoggingMixin
from ..utils.storage_utils import StorageUtils


class SupabaseStorageAdapter(IStorageService, LoggingMixin):
    """Adaptador que hace que StorageUtils implemente IStorageService."""

    def __init__(self, bucket_name: str):
        super().__init__()
        self._storage_utils = StorageUtils(bucket_name)
        self.logger.debug(
            f"SupabaseStorageAdapter initialized with bucket: {bucket_name}"
        )

    def upload_item(self, file_path: str, file_obj) -> bool:
        """Sube un archivo y retorna True si fue exitoso, False en caso contrario."""
        result = self._storage_utils.upload_item(file_path, file_obj)
        if result:
            self.logger.info(f"File uploaded to: {file_path}")
            return True
        else:
            self.logger.error("File upload failed.")
            return False

    def get_item_url(self, file_path: str) -> str | None:
        """Obtiene la URL pública de un archivo."""
        self.logger.debug(f"Getting public URL for file: {file_path}")
        return self._storage_utils.get_item_url(file_path)

    def delete_item(self, file_path: str) -> bool:
        """Elimina un archivo."""
        self.logger.debug(f"Deleting file: {file_path}")
        return self._storage_utils.delete_item(file_path)
