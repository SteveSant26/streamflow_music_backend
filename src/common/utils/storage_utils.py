from typing import Optional

from django.conf import settings
from supabase import Client, create_client

from .logging_config import get_logger

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
            # Verificar que file_obj tiene método read
            if not hasattr(file_obj, "read"):
                logger.error("[Upload] El objeto file no tiene método read")
                return False

            # Leer el contenido del archivo
            file_content_obj = file_obj.read()

            # Verificar que hay contenido
            if not file_content_obj:
                logger.error("[Upload] El archivo está vacío")
                return False

            logger.info(f"[Upload] Subiendo archivo a: {self.bucket_name}/{file_path}")
            logger.debug(f"[Upload] Tamaño del archivo: {len(file_content_obj)} bytes")

            # Verificar conexión a Supabase
            if not self.supabase:
                logger.error("[Upload] Cliente de Supabase no inicializado")
                return False

            upload_response = self.supabase.storage.from_(self.bucket_name).upload(
                file_path,
                file_content_obj,
                file_options={"cache-control": "3600", "upsert": str(upsert).lower()},  # type: ignore
            )
            logger.debug(f"[Upload] Respuesta de Supabase: {upload_response}")

            # Verificar diferentes tipos de errores en la respuesta
            if hasattr(upload_response, "__dict__"):
                response_dict = upload_response.__dict__
                if "error" in response_dict and response_dict.get("error"):
                    logger.error(
                        f"[Upload] Error en respuesta de Supabase: {response_dict['error']}"
                    )
                    return False

            # Verificar si la respuesta contiene información de error en el diccionario
            if isinstance(upload_response, dict) and "error" in upload_response:
                logger.error(
                    f"[Upload] Error en respuesta de Supabase: {upload_response['error']}"
                )
                return False

            logger.info(f"[Upload] Archivo subido exitosamente: {file_path}")

            # Verificar que el archivo existe en el bucket
            try:
                public_url = self.supabase.storage.from_(
                    self.bucket_name
                ).get_public_url(file_path)
                logger.debug(f"[Upload] URL pública generada: {public_url}")
            except Exception as url_error:
                logger.warning(f"[Upload] No se pudo generar URL pública: {url_error}")

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
