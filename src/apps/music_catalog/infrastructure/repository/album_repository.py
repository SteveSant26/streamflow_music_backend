from typing import List, Optional
from django.db.models import Q

from apps.music_catalog.domain.repository.Imusic_repository import IAlbumRepository
from apps.music_catalog.domain.entities import AlbumEntity
from ..models import Album
from src.common.utils import get_logger

logger = get_logger(__name__)


class AlbumRepository(IAlbumRepository):
    """Implementación del repositorio de álbumes"""
    
    def get_by_id(self, entity_id: str) -> Optional[AlbumEntity]:
        try:
            album = Album.objects.select_related('artist').get(
                id=entity_id, is_active=True
            )
            return self._model_to_entity(album)
        except Album.DoesNotExist:
            return None
    
    def get_all(self) -> List[AlbumEntity]:
        albums = Album.objects.select_related('artist').filter(
            is_active=True
        ).order_by('-release_date', 'title')
        return [self._model_to_entity(album) for album in albums]
    
    def get_by_artist(self, artist_id: str) -> List[AlbumEntity]:
        albums = Album.objects.select_related('artist').filter(
            artist_id=artist_id, is_active=True
        ).order_by('-release_date', 'title')
        return [self._model_to_entity(album) for album in albums]
    
    def get_by_genre(self, genre_id: str) -> List[AlbumEntity]:
        """Obtiene álbumes por género"""
        albums = Album.objects.select_related('artist').filter(
            songs__genre_id=genre_id, is_active=True
        ).distinct().order_by('-release_date', 'title')
        return [self._model_to_entity(album) for album in albums]
    
    def get_recent_releases(self, limit: int = 20) -> List[AlbumEntity]:
        """Obtiene álbumes recientes"""
        albums = Album.objects.select_related('artist').filter(
            is_active=True
        ).order_by('-release_date', 'title')[:limit]
        return [self._model_to_entity(album) for album in albums]
    
    def search_by_title(self, title: str) -> List[AlbumEntity]:
        albums = Album.objects.select_related('artist').filter(
            Q(title__icontains=title) & Q(is_active=True)
        ).order_by('-release_date', 'title')[:50]
        return [self._model_to_entity(album) for album in albums]
    
    def get_popular_albums(self, limit: int = 50) -> List[AlbumEntity]:
        albums = Album.objects.select_related('artist').filter(
            is_active=True
        ).order_by('-play_count', 'title')[:limit]
        return [self._model_to_entity(album) for album in albums]
    
    def save(self, entity: AlbumEntity) -> AlbumEntity:
        album_data = self._entity_to_model_data(entity)
        album, created = Album.objects.update_or_create(
            id=entity.id,
            defaults=album_data
        )
        return self._model_to_entity(album)
    
    def delete(self, entity_id: str) -> None:
        Album.objects.filter(id=entity_id).update(is_active=False)
    
    def update(self, entity_id: str, entity: AlbumEntity) -> AlbumEntity:
        album_data = self._entity_to_model_data(entity)
        Album.objects.filter(id=entity_id).update(**album_data)
        updated_album = Album.objects.select_related('artist').get(id=entity_id)
        return self._model_to_entity(updated_album)
    
    def _model_to_entity(self, model: Album) -> AlbumEntity:
        return AlbumEntity(
            id=str(model.id),
            title=model.title,
            artist_id=str(model.artist.id),
            artist_name=model.artist.name,
            release_date=model.release_date,
            description=model.description,
            cover_image_url=model.cover_image_url,
            total_tracks=model.total_tracks,
            play_count=model.play_count,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _entity_to_model_data(self, entity: AlbumEntity) -> dict:
        return {
            'title': entity.title,
            'artist_id': entity.artist_id,
            'release_date': entity.release_date,
            'description': entity.description,
            'cover_image_url': entity.cover_image_url,
            'total_tracks': entity.total_tracks,
            'play_count': entity.play_count,
            'is_active': entity.is_active
        }
    
    def _entity_to_model(self, entity: AlbumEntity) -> Album:
        # Para compatibilidad con IBaseRepository
        pass
