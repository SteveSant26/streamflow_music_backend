from typing import List

from asgiref.sync import sync_to_async

from apps.albums.api.mappers import AlbumEntityModelMapper
from apps.albums.domain.repository import IAlbumRepository
from common.core import BaseDjangoRepository

from ...domain.entities import AlbumEntity
from ..models import AlbumModel


class AlbumRepository(BaseDjangoRepository[AlbumEntity, AlbumModel], IAlbumRepository):
    """Implementación del repositorio de álbumes"""

    def __init__(self):
        super().__init__(AlbumModel, AlbumEntityModelMapper())

    async def find_by_artist_id(
        self, artist_id: str, limit: int = 10
    ) -> List[AlbumEntity]:
        """Busca álbumes por ID del artista"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.filter(
                    artist_id=artist_id,
                ).order_by(
                    "-release_date"
                )[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def search_by_title(self, title: str, limit: int = 10) -> List[AlbumEntity]:
        """Busca álbumes por título"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.filter(
                    title__icontains=title,
                ).order_by(
                    "-play_count"
                )[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)

    async def get_recent_albums(self, limit: int = 10) -> List[AlbumEntity]:
        """Obtiene álbumes recientes"""
        models = await sync_to_async(
            lambda: list(self.model_class.objects.all().order_by("-created_at")[:limit])
        )()
        return self.mapper.models_to_entities(models)

    async def get_popular_albums(self, limit: int = 10) -> List[AlbumEntity]:
        """Obtiene álbumes populares"""
        models = await sync_to_async(
            lambda: list(self.model_class.objects.all().order_by("-play_count")[:limit])
        )()
        return self.mapper.models_to_entities(models)

    async def find_by_release_year(
        self, year: int, limit: int = 10
    ) -> List[AlbumEntity]:
        """Busca álbumes por año de lanzamiento"""
        models = await sync_to_async(
            lambda: list(
                self.model_class.objects.filter(
                    release_date__year=year,
                ).order_by(
                    "-play_count"
                )[:limit]
            )
        )()
        return self.mapper.models_to_entities(models)
