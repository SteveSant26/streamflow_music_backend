import uuid
from typing import Optional

from django.utils import timezone

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class SaveArtistUseCase(BaseUseCase[dict, Optional[ArtistEntity]]):
    """Caso de uso para guardar un artista"""

    def __init__(self, artist_repository: IArtistRepository):
        super().__init__()
        self.artist_repository = artist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(self, artist_data: dict) -> Optional[ArtistEntity]:
        """
        Guarda un artista desde datos externos como YouTube

        Args:
            artist_data: Diccionario con datos del artista
                - name (str): Nombre del artista
                - image_url (str, opcional): URL de la imagen
                - source_type (str, opcional): Tipo de fuente (youtube, spotify, etc.)
                - source_id (str, opcional): ID en la fuente externa
                - source_url (str, opcional): URL en la fuente externa
                - channel_id (str, opcional): ID del canal de YouTube (para compatibilidad)
                - channel_url (str, opcional): URL del canal (para compatibilidad)

        Returns:
            Entidad de artista guardada o None si falla
        """
        try:
            name = artist_data.get("name")
            if not name:
                self.logger.error("Artist name is required")
                return None

            # Normalizar datos de entrada
            source_type = artist_data.get("source_type", "youtube")
            source_id = artist_data.get("source_id") or artist_data.get("channel_id")
            source_url = artist_data.get("source_url") or artist_data.get("channel_url")
            image_url = artist_data.get("image_url")

            # Si tenemos información de fuente, verificar si ya existe
            if source_type and source_id:
                existing_artist = await self.artist_repository.get_by_source(
                    source_type, source_id
                )
                if existing_artist:
                    self.logger.info(
                        f"Artist '{name}' already exists from {source_type}: {source_id}"
                    )
                    return existing_artist

            # Buscar por nombre como fallback
            existing_artist = await self.artist_repository.find_by_name(name)
            if existing_artist:
                # Si encontramos el artista por nombre pero no tiene información de fuente,
                # actualizamos los metadatos de fuente
                if source_type and source_id and not existing_artist.source_id:
                    existing_artist.source_type = source_type
                    existing_artist.source_id = source_id
                    existing_artist.source_url = source_url
                    existing_artist.updated_at = timezone.now()
                    updated_artist = await self.artist_repository.save(existing_artist)
                    self.logger.info(f"Updated artist '{name}' with source information")
                    return updated_artist

                self.logger.info(f"Artist '{name}' already exists by name")
                return existing_artist

            # Crear nuevo artista
            artist_entity = ArtistEntity(
                id=str(uuid.uuid4()),
                name=name,
                image_url=image_url,
                source_type=source_type,
                source_id=source_id,
                source_url=source_url,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            saved_artist = await self.artist_repository.save(artist_entity)
            self.logger.info(f"✅ Created new artist: {name} (ID: {saved_artist.id})")
            return saved_artist

        except Exception as e:
            self.logger.error(f"Error saving artist: {str(e)}")
            return None
