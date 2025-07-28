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

    def upload_item(
        self, file_path: str, file_obj, upsert: bool = True
    ) -> Optional[str]:
        if not file_path or not file_obj:
            logger.error("[Upload] Ruta del archivo o el archivo en sí están ausentes.")
            return None

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
                return None

            return self.get_item_url(file_path)

        except Exception as e:
            logger.exception(f"[Upload] Error inesperado al subir archivo: {e}")
            return None

    def get_item_url(self, file_path: str) -> Optional[str]:
        """
        file_path: ruta del archivo dentro del bucket, ej: "multimedia/user123/audio.mp3"
        """
        try:
            if file_path:
                url = self.supabase.storage.from_(self.bucket_name).get_public_url(
                    file_path
                )
                logger.info(f"[URL] URL pública generada para: {file_path}")
                return url
            logger.warning("[URL] file_path vacío o nulo.")
            return None
        except Exception as e:
            logger.exception(f"[URL] Error al generar URL pública: {e}")
            return None

    def delete_item(self, file_path: str) -> bool:
        """
        Elimina un archivo del bucket de Supabase Storage
        """
        try:
            if file_path:
                logger.info(f"[Delete] Eliminando archivo: {file_path}")
                response = self.supabase.storage.from_(self.bucket_name).remove(
                    [file_path]
                )

                if any("error" in res and res["error"] for res in response):
                    logger.error(f"[Delete] Error al eliminar archivo: {response}")
                    return False

                logger.info(f"[Delete] Archivo eliminado exitosamente: {file_path}")
                return True

            logger.warning("[Delete] file_path vacío o nulo.")
            return False
        except Exception as e:
            logger.exception(f"[Delete] Error inesperado al eliminar archivo: {e}")
            return False
