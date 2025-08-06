import uuid
from typing import Optional, cast

from django.utils import timezone

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import AlbumEntity
from ..domain.repository import IAlbumRepository
from ..infrastructure.repository.album_repository import AlbumRepository


class SaveAlbumUseCase(BaseUseCase[dict, Optional[AlbumEntity]]):
    """Caso de uso para guardar un álbum"""

    def __init__(self, album_repository: IAlbumRepository):
        super().__init__()
        self.album_repository = album_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    def execute(self, album_data: dict) -> Optional[AlbumEntity]:
        """
        Guarda un álbum desde datos externos

        Args:
            album_data: Diccionario con datos del álbum
                - title (str): Título del álbum
                - artist_id (str): ID del artista
                - artist_name (str): Nombre del artista
                - cover_image_url (str, opcional): URL de la portada

        Returns:
            Entidad de álbum guardada o None si falla
        """
        try:
            title = album_data.get("title")
            artist_id = album_data.get("artist_id")
            artist_name = album_data.get("artist_name")

            if not title or not artist_id or not artist_name:
                self.logger.error("Album title, artist_id and artist_name are required")
                return None

            # Obtener datos de entrada
            cover_image_url = album_data.get("cover_image_url")

            # Buscar por título y artista o crear nuevo
            existing_album = self.album_repository.find_or_create_by_title_and_artist(
                title, artist_id, artist_name, cover_image_url
            )

            if existing_album:
                self.logger.info(f"Album '{title}' by {artist_name} found or created")
                return existing_album

            # Si falla la creación mediante find_or_create, crear manualmente
            album_entity = AlbumEntity(
                id=str(uuid.uuid4()),
                title=title,
                artist_id=artist_id,
                artist_name=artist_name,
                cover_image_url=cover_image_url,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            saved_album = cast(AlbumRepository, self.album_repository).save(
                album_entity
            )
            self.logger.info(
                f"✅ Created new album: {title} by {artist_name} (ID: {saved_album.id})"
            )
            return saved_album

        except Exception as e:
            self.logger.error(f"Error saving album: {str(e)}")
            return None
