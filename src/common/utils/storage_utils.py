from typing import Optional

from django.conf import settings
from supabase import Client, create_client

from src.common.utils import get_logger

logger = get_logger(__name__)


class StorageUtils:
    def __init__(self, bucket_name: str):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY
        )
        self.bucket_name = bucket_name

    def upload_item(self, file_path: str, file_obj, upsert: bool = True) -> bool:
        """
        Sube un archivo a Supabase Storage.

        Returns:
            bool: True si la subida fue exitosa, False en caso contrario
        """
        if not file_path or not file_obj:
            logger.error("[Upload] Ruta del archivo o el archivo en sí están ausentes.")
            return False

        try:
            file_content_obj = file_obj.read()

            logger.info(f"[Upload] Subiendo archivo a: {self.bucket_name}/{file_path}")

            upload_response = self.supabase.storage.from_(self.bucket_name).upload(
                file_path,
                file_content_obj,
                file_options={"cache-control": "3600", "upsert": str(upsert).lower()},  # type: ignore
            )
            logger.debug(f"[Upload] Respuesta de Supabase: {upload_response}")

            err = getattr(upload_response, "error", None)
            if err:
                logger.error(f"[Upload] Error al subir el archivo: {err}")
                return False

            logger.info(f"[Upload] Archivo subido exitosamente: {file_path}")
            return True

        except Exception as e:
            logger.exception(f"[Upload] Error inesperado al subir archivo: {e}")
            return False

    def get_item_url(self, file_path: str) -> Optional[str]:
        """
        file_path: ruta del archivo dentro del bucket, ej: "user123.jpg"
        o ruta completa "profile-pictures/user123.jpg"
        o una URL completa que se devuelve tal como está.
        """
        try:
            if file_path:
                # Si ya es una URL (http/https), devolverla tal como está
                if file_path.startswith(("http://", "https://")):
                    logger.info(f"[URL] URL ya completa, devolviendo: {file_path}")
                    return file_path

                # Limpiar la ruta si incluye el bucket name duplicado
                clean_path = self._clean_file_path(file_path)

                # Si no es una URL, generar la URL pública desde Supabase
                url = self.supabase.storage.from_(self.bucket_name).get_public_url(
                    clean_path
                )
                logger.info(f"[URL] URL pública generada para: {clean_path}")
                return url
            logger.warning("[URL] file_path vacío o nulo.")
            return None
        except Exception as e:
            logger.exception(f"[URL] Error al generar URL pública: {e}")
            return None

    def _clean_file_path(self, file_path: str) -> str:
        """
        Limpia la ruta del archivo removiendo el bucket name si está duplicado.
        Ej: "profile-pictures/user_123.jpg" -> "user_123.jpg"
        """
        bucket_prefix = f"{self.bucket_name}/"
        if file_path.startswith(bucket_prefix):
            clean_path = file_path[len(bucket_prefix) :]
            logger.debug(
                f"[Clean Path] Removed bucket prefix: {file_path} -> {clean_path}"
            )
            return clean_path
        return file_path

    def delete_item(self, file_path: str) -> bool:
        """
        Elimina un archivo del bucket de Supabase Storage
        """
        try:
            if file_path:
                # Limpiar la ruta si incluye el bucket name duplicado
                clean_path = self._clean_file_path(file_path)

                logger.info(f"[Delete] Eliminando archivo: {clean_path}")
                response = self.supabase.storage.from_(self.bucket_name).remove(
                    [clean_path]
                )

                if any("error" in res and res["error"] for res in response):
                    logger.error(f"[Delete] Error al eliminar archivo: {response}")
                    return False

                logger.info(f"[Delete] Archivo eliminado exitosamente: {clean_path}")
                return True

            logger.warning("[Delete] file_path vacío o nulo.")
            return False
        except Exception as e:
            logger.exception(f"[Delete] Error inesperado al eliminar archivo: {e}")
            return False
