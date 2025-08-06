import uuid
from typing import List, Optional

from asgiref.sync import sync_to_async
from django.utils import timezone

from apps.albums.api.mappers import AlbumEntityModelMapper
from apps.albums.domain.repository import IAlbumRepository
from common.core import BaseDjangoRepository

from ...domain.entities import AlbumEntity
from ..models import AlbumModel


class AlbumRepository(BaseDjangoRepository[AlbumEntity, AlbumModel], IAlbumRepository):
    """Implementación del repositorio de álbumes"""

    def __init__(self):
        super().__init__(AlbumModel, AlbumEntityModelMapper())

    def save(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, entity: AlbumEntity
    ) -> AlbumEntity:
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

    async def find_by_artist_id(
        self, artist_id: str, limit: int = 10
    ) -> List[AlbumEntity]:
        """Busca álbumes por ID del artista"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.select_related("artist")
                .filter(
                    artist__id=artist_id,
                )
                .order_by("-release_date")[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def search_by_title(self, title: str, limit: int = 10) -> List[AlbumEntity]:
        """Busca álbumes por título"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.select_related("artist")
                .filter(
                    title__icontains=title,
                )
                .order_by("-play_count")[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def get_recent_albums(self, limit: int = 10) -> List[AlbumEntity]:
        """Obtiene álbumes recientes"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.select_related("artist")
                .all()
                .order_by("-created_at")[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def get_popular_albums(self, limit: int = 10) -> List[AlbumEntity]:
        """Obtiene álbumes populares"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.select_related("artist")
                .all()
                .order_by("-play_count")[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def find_by_release_year(
        self, year: int, limit: int = 10
    ) -> List[AlbumEntity]:
        """Busca álbumes por año de lanzamiento"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.select_related("artist")
                .filter(
                    release_date__year=year,
                )
                .order_by("-play_count")[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)

    def find_or_create_by_title_and_artist(
        self,
        title: str,
        artist_id: str,
        artist_name: str,
        cover_image_url: Optional[str] = None,
    ) -> AlbumEntity:
        """Busca un álbum por título y artista, si no existe lo crea (versión síncrona)"""
        # Primero intentar encontrar por título y artista
        try:
            model = self.model_class.objects.select_related("artist").get(
                title__iexact=title, artist__id=artist_id
            )
            return self.mapper.model_to_entity(model)
        except self.model_class.DoesNotExist:
            # Si no existe, crear uno nuevo
            album_entity = AlbumEntity(
                id=str(uuid.uuid4()),
                title=title,
                artist_id=artist_id,
                artist_name=artist_name,
                cover_image_url=cover_image_url,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

        return self.save(album_entity)

    async def get_by_source(
        self, source_type: str, source_id: str
    ) -> Optional[AlbumEntity]:
        """Busca un álbum por fuente externa"""
        try:
            model = await self.model_class.objects.select_related("artist").aget(
                source_type=source_type, source_id=source_id
            )
            return self.mapper.model_to_entity(model)
        except self.model_class.DoesNotExist:
            return None
