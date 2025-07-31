from typing import List, cast

from django.db.models import Q

from apps.music_catalog.domain.entities import AlbumEntity
from apps.music_catalog.domain.repository.Ialbum_repository import IAlbumRepository
from src.common.core import BaseDjangoRepository

from ..models import AlbumModel


class AlbumRepository(BaseDjangoRepository[AlbumEntity, AlbumModel], IAlbumRepository):
    """
    Implementación del repositorio de álbumes que combina funcionalidades
    de solo lectura y solo escritura, implementando la interfaz IAlbumRepository.
    """

    def __init__(self):
        super().__init__(AlbumModel)

    # Métodos específicos del repositorio de álbumes (implementación de IAlbumRepository)

    def get_by_artist(self, artist_id: str) -> List[AlbumEntity]:
        """Obtiene álbumes por artista"""
        albums = (
            AlbumModel.objects.select_related("artist")
            .filter(artist_id=artist_id, is_active=True)
            .order_by("-release_date")
        )
        return [self._model_to_entity(album) for album in albums]

    def get_by_genre(self, genre_id: str) -> List[AlbumEntity]:
        """Obtiene álbumes por género"""
        albums = (
            AlbumModel.objects.select_related("artist")
            .filter(songs__genre_id=genre_id, is_active=True)
            .distinct()
            .order_by("-release_date")
        )
        return [self._model_to_entity(album) for album in albums]

    def search_by_title(self, title: str) -> List[AlbumEntity]:
        """Busca álbumes por título"""
        albums = (
            AlbumModel.objects.select_related("artist")
            .filter(Q(title__icontains=title) & Q(is_active=True))
            .order_by("-release_date")[:50]
        )
        return [self._model_to_entity(album) for album in albums]

    def get_recent_releases(self, limit: int = 20) -> List[AlbumEntity]:
        """Obtiene álbumes recientes"""
        albums = (
            AlbumModel.objects.select_related("artist")
            .filter(is_active=True)
            .order_by("-release_date")[:limit]
        )
        return [self._model_to_entity(album) for album in albums]

    # Implementación de métodos abstractos del repositorio base

    def _model_to_entity(self, model: AlbumModel) -> AlbumEntity:
        """Convierte un modelo Album a entidad AlbumEntity"""
        album_model = cast(AlbumModel, model)
        return AlbumEntity(
            id=str(album_model.id),
            title=album_model.title,
            artist_id=str(album_model.artist.id),
            artist_name=album_model.artist.name,
            release_date=album_model.release_date,
            description=None,  # Campo no disponible en el modelo
            cover_image_url=album_model.cover_image_url,
            total_tracks=album_model.total_tracks,
            play_count=0,  # Campo no disponible en el modelo, usar valor por defecto
            is_active=album_model.is_active,
            created_at=album_model.created_at,
            updated_at=album_model.updated_at,
        )

    def _entity_to_model_data(self, entity: AlbumEntity) -> dict:
        """Convierte una entidad AlbumEntity a datos del modelo"""
        return {
            "title": entity.title,
            "artist_id": entity.artist_id,
            "release_date": entity.release_date,
            "cover_image_url": entity.cover_image_url,
            "total_tracks": entity.total_tracks,
            "is_active": entity.is_active,
        }

    def _entity_to_model(self, entity: AlbumEntity) -> AlbumModel:
        """Convierte una entidad AlbumEntity a un modelo Django Album"""
        try:
            album_data = {
                "title": entity.title,
                "artist_id": entity.artist_id,
                "release_date": entity.release_date,
                "cover_image_url": entity.cover_image_url,
                "total_tracks": entity.total_tracks,
                "is_active": entity.is_active,
            }

            # Si la entidad tiene un id (álbum existente), incluirlo
            if hasattr(entity, "id") and entity.id is not None:
                album_data["id"] = entity.id

            album = AlbumModel(**album_data)
            return album

        except Exception as e:
            self.logger.error(f"Error al convertir entidad álbum a modelo: {str(e)}")
            raise

    def _apply_default_ordering(self, queryset):
        """Aplica ordenamiento específico para álbumes"""
        return queryset.order_by("-release_date")
