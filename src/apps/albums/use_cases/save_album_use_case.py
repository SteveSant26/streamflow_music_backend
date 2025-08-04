import uuid
from typing import Optional

from django.utils import timezone

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import AlbumEntity
from ..domain.repository import IAlbumRepository


class SaveAlbumUseCase(BaseUseCase[dict, Optional[AlbumEntity]]):
    """Caso de uso para guardar un álbum"""

    def __init__(self, album_repository: IAlbumRepository):
        super().__init__()
        self.album_repository = album_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(self, album_data: dict) -> Optional[AlbumEntity]:
        """
        Guarda un álbum desde datos externos

        Args:
            album_data: Diccionario con datos del álbum
                - title (str): Título del álbum
                - artist_id (str): ID del artista
                - artist_name (str): Nombre del artista
                - cover_image_url (str, opcional): URL de la portada
                - source_type (str, opcional): Tipo de fuente (youtube, spotify, etc.)
                - source_id (str, opcional): ID en la fuente externa
                - source_url (str, opcional): URL en la fuente externa

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

            # Normalizar datos de entrada
            source_type = album_data.get("source_type", "youtube")
            source_id = album_data.get("source_id")
            source_url = album_data.get("source_url")
            cover_image_url = album_data.get("cover_image_url")

            # Si tenemos información de fuente, verificar si ya existe
            if source_type and source_id:
                existing_album = await self.album_repository.get_by_source(
                    source_type, source_id
                )
                if existing_album:
                    self.logger.info(
                        f"Album '{title}' already exists from {source_type}: {source_id}"
                    )
                    return existing_album

            # Buscar por título y artista como fallback
            existing_album = (
                await self.album_repository.find_or_create_by_title_and_artist(
                    title, artist_id, artist_name, cover_image_url
                )
            )

            # Si el álbum existía pero no tiene información de fuente, actualizarla
            if (
                existing_album
                and source_type
                and source_id
                and not existing_album.source_id
            ):
                existing_album.source_type = source_type
                existing_album.source_id = source_id
                existing_album.source_url = source_url
                existing_album.updated_at = timezone.now()
                updated_album = await self.album_repository.save(existing_album)
                self.logger.info(f"Updated album '{title}' with source information")
                return updated_album

            # Si encontramos un álbum existente por título/artista
            if existing_album:
                self.logger.info(f"Album '{title}' by {artist_name} already exists")
                return existing_album

            # Crear nuevo álbum
            album_entity = AlbumEntity(
                id=str(uuid.uuid4()),
                title=title,
                artist_id=artist_id,
                artist_name=artist_name,
                cover_image_url=cover_image_url,
                source_type=source_type,
                source_id=source_id,
                source_url=source_url,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            saved_album = await self.album_repository.save(album_entity)
            self.logger.info(
                f"✅ Created new album: {title} by {artist_name} (ID: {saved_album.id})"
            )
            return saved_album

        except Exception as e:
            self.logger.error(f"Error saving album: {str(e)}")
            return None
