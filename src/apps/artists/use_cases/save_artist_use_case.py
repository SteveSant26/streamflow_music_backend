import uuid
from typing import Optional, cast

from django.utils import timezone

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository
from ..infrastructure.repository.artist_repository import ArtistRepository


class SaveArtistUseCase(BaseUseCase[dict, Optional[ArtistEntity]]):
    """Caso de uso para guardar un artista"""

    def __init__(self, artist_repository: IArtistRepository):
        super().__init__()
        self.artist_repository = artist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    def execute(self, artist_data: dict) -> Optional[ArtistEntity]:
        """
        Guarda un artista desde datos externos

        Args:
            artist_data: Diccionario con datos del artista
                - name (str): Nombre del artista
                - image_url (str, opcional): URL de la imagen

        Returns:
            Entidad de artista guardada o None si falla
        """
        try:
            name = artist_data.get("name")
            if not name:
                self.logger.error("Artist name is required")
                return None

            # Obtener datos de entrada
            image_url = artist_data.get("image_url")

            # Buscar si ya existe el artista por nombre
            existing_artist = cast(
                ArtistRepository, self.artist_repository
            ).find_by_name(name)
            if existing_artist:
                self.logger.info(f"Artist '{name}' already exists")
                return existing_artist

            # Crear nuevo artista
            artist_entity = ArtistEntity(
                id=str(uuid.uuid4()),
                name=name,
                image_url=image_url,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            saved_artist = cast(ArtistRepository, self.artist_repository).save(
                artist_entity
            )
            self.logger.info(f"✅ Created new artist: {name} (ID: {saved_artist.id})")
            return saved_artist

        except Exception as e:
            self.logger.error(f"Error saving artist: {str(e)}")
            return None
