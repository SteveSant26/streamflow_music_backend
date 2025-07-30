from typing import List, Optional
from django.db.models import Q
from django.core.paginator import Paginator

from apps.music_catalog.domain.repository.Imusic_repository import (
    ISongRepository, 
    IArtistRepository, 
    IAlbumRepository, 
    IGenreRepository,
    IMusicSearchRepository
)
from apps.music_catalog.domain.entities import (
    SongEntity, 
    ArtistEntity, 
    AlbumEntity, 
    GenreEntity,
    SearchResultEntity,
    PaginatedResultEntity
)
from ..models import Song, Artist, Album, Genre
from src.common.utils import get_logger

logger = get_logger(__name__)


class SongRepository(ISongRepository):
    """Implementación del repositorio de canciones"""
    
    def get_by_id(self, entity_id: str) -> Optional[SongEntity]:
        try:
            song = Song.objects.select_related('artist', 'album', 'genre').get(
                id=entity_id, is_active=True
            )
            return self._model_to_entity(song)
        except Song.DoesNotExist:
            return None
    
    def get_all(self) -> List[SongEntity]:
        songs = Song.objects.select_related('artist', 'album', 'genre').filter(
            is_active=True
        ).order_by('title')
        return [self._model_to_entity(song) for song in songs]
    
    def get_by_artist(self, artist_id: str) -> List[SongEntity]:
        songs = Song.objects.select_related('artist', 'album', 'genre').filter(
            artist_id=artist_id, is_active=True
        ).order_by('album__release_date', 'track_number', 'title')
        return [self._model_to_entity(song) for song in songs]
    
    def get_by_album(self, album_id: str) -> List[SongEntity]:
        songs = Song.objects.select_related('artist', 'album', 'genre').filter(
            album_id=album_id, is_active=True
        ).order_by('track_number', 'title')
        return [self._model_to_entity(song) for song in songs]
    
    def get_by_genre(self, genre_id: str) -> List[SongEntity]:
        songs = Song.objects.select_related('artist', 'album', 'genre').filter(
            genre_id=genre_id, is_active=True
        ).order_by('-play_count', 'title')
        return [self._model_to_entity(song) for song in songs]
    
    def search_by_title(self, title: str) -> List[SongEntity]:
        songs = Song.objects.select_related('artist', 'album', 'genre').filter(
            Q(title__icontains=title) & Q(is_active=True)
        ).order_by('-play_count', 'title')[:50]
        return [self._model_to_entity(song) for song in songs]
    
    def get_popular_songs(self, limit: int = 50) -> List[SongEntity]:
        songs = Song.objects.select_related('artist', 'album', 'genre').filter(
            is_active=True
        ).order_by('-play_count', 'title')[:limit]
        return [self._model_to_entity(song) for song in songs]
    
    def increment_play_count(self, song_id: str) -> bool:
        try:
            song = Song.objects.get(id=song_id, is_active=True)
            song.increment_play_count()
            return True
        except Song.DoesNotExist:
            return False
    
    def save(self, entity: SongEntity) -> SongEntity:
        # Implementación de guardado (para crear/actualizar canciones)
        song_data = self._entity_to_model_data(entity)
        song, created = Song.objects.update_or_create(
            id=entity.id,
            defaults=song_data
        )
        return self._model_to_entity(song)
    
    def delete(self, entity_id: str) -> None:
        Song.objects.filter(id=entity_id).update(is_active=False)
    
    def update(self, entity_id: str, entity: SongEntity) -> SongEntity:
        song_data = self._entity_to_model_data(entity)
        Song.objects.filter(id=entity_id).update(**song_data)
        updated_song = Song.objects.select_related('artist', 'album', 'genre').get(id=entity_id)
        return self._model_to_entity(updated_song)
    
    def _model_to_entity(self, model: Song) -> SongEntity:
        return SongEntity(
            id=str(model.id),
            title=model.title,
            artist_id=str(model.artist.id),
            artist_name=model.artist.name,
            album_id=str(model.album.id) if model.album else None,
            album_title=model.album.title if model.album else None,
            duration_seconds=model.duration_seconds,
            file_url=model.file_url,
            lyrics=model.lyrics,
            track_number=model.track_number,
            genre_id=str(model.genre.id) if model.genre else None,
            genre_name=model.genre.name if model.genre else None,
            play_count=model.play_count,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _entity_to_model_data(self, entity: SongEntity) -> dict:
        data = {
            'title': entity.title,
            'artist_id': entity.artist_id,
            'duration_seconds': entity.duration_seconds,
            'file_url': entity.file_url,
            'lyrics': entity.lyrics,
            'track_number': entity.track_number,
            'play_count': entity.play_count,
            'is_active': entity.is_active
        }
        if entity.album_id:
            data['album_id'] = entity.album_id
        if entity.genre_id:
            data['genre_id'] = entity.genre_id
        return data
    
    def _entity_to_model(self, entity: SongEntity) -> Song:
        # Para compatibilidad con IBaseRepository
        pass
