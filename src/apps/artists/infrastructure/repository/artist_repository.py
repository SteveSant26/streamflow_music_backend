from typing import Optional

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

    def save(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, entity: ArtistEntity
    ) -> ArtistEntity:
        try:
            model_data = self.mapper.entity_to_model_data(entity)

            model_instance, created = self.model_class.objects.update_or_create(
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

    def find_by_name(self, name: str) -> Optional[ArtistEntity]:
        """Busca un artista por nombre exacto"""
        try:
            model = self.model_class.objects.get(
                name__iexact=name,
            )
            return self.mapper.model_to_entity(model)
        except self.model_class.DoesNotExist:
            return None
