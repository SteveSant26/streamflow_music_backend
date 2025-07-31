from abc import ABC, abstractmethod


class IStorageService(ABC):
    """Interface para servicios de almacenamiento."""

    @abstractmethod
    def upload_item(self, file_path: str, file_obj) -> bool:
        """Sube un archivo y retorna True si fue exitoso, False en caso contrario."""

    @abstractmethod
    def get_item_url(self, file_path: str) -> str | None:
        """Obtiene la URL pública de un archivo."""

    @abstractmethod
    def delete_item(self, file_path: str) -> bool:
        """Elimina un archivo."""
