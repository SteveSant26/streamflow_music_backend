<<<<<<< HEAD
import uuid
from typing import List, Optional

from asgiref.sync import sync_to_async
from django.utils import timezone

=======
from typing import Optional

>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
from apps.artists.api.mappers import ArtistEntityModelMapper
from apps.artists.domain.repository import IArtistRepository
from common.core import BaseDjangoRepository

from ...domain.entities import ArtistEntity
from ..models import ArtistModel


class ArtistRepository(
    BaseDjangoRepository[ArtistEntity, ArtistModel], IArtistRepository
):
    """Implementación del repositorio de artistas"""

    def __init__(self):
        super().__init__(ArtistModel, ArtistEntityModelMapper())

<<<<<<< HEAD
=======
    async def save(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, entity: ArtistEntity
    ) -> ArtistEntity:
        try:
            model_data = self.mapper.entity_to_model_data(entity)

            model_instance, created = await self.model_class.objects.aupdate_or_create(
                id=getattr(entity, "id", None), defaults=model_data
            )

            action = "created" if created else "updated"
            self.logger.info(
                f"{self.model_class.__name__} {action} with id {model_instance.pk}"
            )
            return self.mapper.model_to_entity(model_instance)
        except Exception as e:
            self.logger.error(f"Error saving {self.model_class.__name__}: {str(e)}")
            raise

>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
    async def find_by_name(self, name: str) -> Optional[ArtistEntity]:
        """Busca un artista por nombre exacto"""
        try:
            model = await self.model_class.objects.aget(
                name__iexact=name,
            )
            return self.mapper.model_to_entity(model)
        except self.model_class.DoesNotExist:
            return None
<<<<<<< HEAD

    async def search_by_name(self, name: str, limit: int = 10) -> List[ArtistEntity]:
        """Busca artistas por nombre (búsqueda parcial)"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.filter(
                    name__icontains=name,
                ).order_by(
                    "-followers_count"
                )[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def find_by_country(
        self, country: str, limit: int = 10
    ) -> List[ArtistEntity]:
        """Busca artistas por país"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.filter(
                    country__iexact=country,
                ).order_by(
                    "-followers_count"
                )[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def get_popular_artists(self, limit: int = 10) -> List[ArtistEntity]:
        """Obtiene los artistas más populares"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.all().order_by("-followers_count")[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def get_verified_artists(self, limit: int = 10) -> List[ArtistEntity]:
        """Obtiene artistas verificados"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.filter(
                    is_verified=True,
                ).order_by(
                    "-followers_count"
                )[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def find_or_create_by_name(
        self, name: str, image_url: Optional[str] = None
    ) -> ArtistEntity:
        """Busca un artista por nombre, si no existe lo crea"""
        # Primero intentar encontrar por nombre
        existing = await self.find_by_name(name)
        if existing:
            return existing

        # Si no existe, crear uno nuevo
        artist_entity = ArtistEntity(
            id=str(uuid.uuid4()),
            name=name,
            image_url=image_url,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        return await self.save(artist_entity)

    async def get_by_source(
        self, source_type: str, source_id: str
    ) -> Optional[ArtistEntity]:
        """Busca un artista por fuente externa (YouTube channel, etc.)"""
        try:
            model = await self.model_class.objects.aget(
                source_type=source_type, source_id=source_id
            )
            return self.mapper.model_to_entity(model)
        except self.model_class.DoesNotExist:
            return None
=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
