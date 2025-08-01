from typing import Any, List

from apps.albums.domain.repository import IAlbumRepository
from common.core import BaseDjangoRepository

from ...domain.entities import AlbumEntity
from ..models import AlbumModel


class AlbumRepository(BaseDjangoRepository[AlbumEntity, AlbumModel], IAlbumRepository):
    """Implementación del repositorio de álbumes"""

    def __init__(self):
        super().__init__(AlbumModel)

    def _model_to_entity(self, model: AlbumModel) -> AlbumEntity:
        """Convierte un modelo Django a entidad del dominio"""
        return AlbumEntity(
            id=str(model.id),
            title=model.title,
            artist_id=str(model.artist_id),
            artist_name=model.artist_name,
            release_date=model.release_date,
            description=model.description,
            cover_image_url=model.cover_image_url,
            total_tracks=model.total_tracks,
            play_count=model.play_count,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model_data(self, entity: AlbumEntity) -> dict[str, Any]:
        """Convierte una entidad a datos del modelo"""
        return {
            "title": entity.title,
            "artist_id": entity.artist_id,
            "artist_name": entity.artist_name,
            "release_date": entity.release_date,
            "description": entity.description,
            "cover_image_url": entity.cover_image_url,
            "total_tracks": entity.total_tracks,
            "play_count": entity.play_count,
            "is_active": entity.is_active,
        }

    def _entity_to_model(self, entity: AlbumEntity) -> AlbumModel:
        """Convierte una entidad AlbumEntity a un modelo Django AlbumModel"""
        try:
            album_data = self._entity_to_model_data(entity)

            if hasattr(entity, "id") and entity.id is not None:
                album_data["id"] = entity.id

            self.logger.debug(f"Convirtiendo entidad álbum a modelo: {album_data}")
            album = AlbumModel(**album_data)
            return album

        except Exception as e:
            self.logger.error(f"Error al convertir entidad álbum a modelo: {str(e)}")
            raise

    async def find_by_artist_id(
        self, artist_id: str, limit: int = 10
    ) -> List[AlbumEntity]:
        """Busca álbumes por ID del artista"""
        models = self.model_class.objects.filter(
            artist_id=artist_id, is_active=True
        ).order_by("-release_date")[:limit]
        return [self._model_to_entity(model) async for model in models]

    async def search_by_title(self, title: str, limit: int = 10) -> List[AlbumEntity]:
        """Busca álbumes por título"""
        models = self.model_class.objects.filter(
            title__icontains=title, is_active=True
        ).order_by("-play_count")[:limit]
        return [self._model_to_entity(model) async for model in models]

    async def get_recent_albums(self, limit: int = 10) -> List[AlbumEntity]:
        """Obtiene álbumes recientes"""
        models = self.model_class.objects.filter(is_active=True).order_by(
            "-created_at"
        )[:limit]
        return [self._model_to_entity(model) async for model in models]

    async def get_popular_albums(self, limit: int = 10) -> List[AlbumEntity]:
        """Obtiene álbumes populares"""
        models = self.model_class.objects.filter(is_active=True).order_by(
            "-play_count"
        )[:limit]
        return [self._model_to_entity(model) async for model in models]

    async def find_by_release_year(
        self, year: int, limit: int = 10
    ) -> List[AlbumEntity]:
        """Busca álbumes por año de lanzamiento"""
        models = self.model_class.objects.filter(
            release_date__year=year, is_active=True
        ).order_by("-play_count")[:limit]
        return [self._model_to_entity(model) async for model in models]
