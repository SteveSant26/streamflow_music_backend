from typing import Optional

from django.conf import settings
from supabase import Client, create_client

from src.common.utils.logging_config import get_logger

logger = get_logger(__name__)


class ImageUtils:
    def __init__(self, bucket_name: str):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY
        )
        self.bucket_name = bucket_name

    def upload_image(
        self, file_path: str, file_obj, upsert: bool = True
    ) -> Optional[str]:
        if not file_path or not file_obj:
            logger.error("File path or file object is missing for upload.")
            return None

        try:
            file_content_obj = file_obj.read()

            logger.info(f"Uploading image to {self.bucket_name}/{file_path}")

            upload_response = self.supabase.storage.from_(self.bucket_name).upload(
                file_path,
                file_content_obj,
                file_options={"cache-control": "3600", "upsert": str(upsert).lower()},  # type: ignore
            )
            logger.info(f"Upload response: {upload_response}")
            err = getattr(upload_response, "error", None)
            if err:
                logger.error(f"Error uploading image: {err}")
                return None

            return self.get_image_url(file_path)

        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            return None

    def get_image_url(self, file_path: str) -> str | None:
        """
        file_path: ruta del archivo dentro del bucket, ej: "profile-photos/user123.jpg"
        """
        try:
            if file_path:
                url = self.supabase.storage.from_(self.bucket_name).get_public_url(
                    file_path
                )
                return url
            return None
        except Exception:
            return None

    def delete_image(self, file_path: str) -> bool:
        """
        Elimina un archivo del bucket de Supabase Storage
        """
        try:
            if file_path:
                response = self.supabase.storage.from_(self.bucket_name).remove(
                    [file_path]
                )
                if any("error" in res and res["error"] for res in response):
                    return False
                return True
            return False
        except Exception:
            return False
