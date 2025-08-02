from typing import List, Optional

from asgiref.sync import sync_to_async
from django.db import models
from django.db.models import Count, Q, Sum

from common.mixins.logging_mixin import LoggingMixin

from ...domain.entities import SongEntity
from ...domain.repository.Isong_repository import ISongRepository
from ..models.song_model import SongModel


class SongRepository(ISongRepository, LoggingMixin):
    """Implementación del repositorio de canciones usando Django ORM"""

    def __init__(self):
        super().__init__()

    async def save(self, song: SongEntity) -> SongEntity:
        """Guarda una canción"""
        try:
            song_data = {
                "title": song.title,
                "album_id": song.album_id,
                "artist_id": song.artist_id,
                "genre_id": song.genre_id,
                "album_title": song.album_title,
                "artist_name": song.artist_name,
                "genre_name": song.genre_name,
                "duration_seconds": song.duration_seconds,
                "track_number": song.track_number,
                "file_url": song.file_url,
                "thumbnail_url": song.thumbnail_url,
                "lyrics": song.lyrics,
                "tags": song.tags or [],
                "play_count": song.play_count,
                "favorite_count": song.favorite_count,
                "download_count": song.download_count,
                "source_type": song.source_type,
                "source_id": song.source_id,
                "source_url": song.source_url,
                "is_explicit": song.is_explicit,
                "is_active": song.is_active,
                "is_premium": song.is_premium,
                "audio_quality": song.audio_quality,
                "last_played_at": song.last_played_at,
                "release_date": song.release_date,
            }

            if song.id:
                # Update existing song - first check if it exists
                try:
                    song_obj = await sync_to_async(SongModel.objects.get)(id=song.id)
                    for key, value in song_data.items():
                        setattr(song_obj, key, value)
                    await sync_to_async(song_obj.save)()
                except SongModel.DoesNotExist:
                    # Song doesn't exist, create it instead
                    self.logger.warning(
                        f"Song with ID {song.id} not found, creating new one"
                    )
                    song_obj = await sync_to_async(SongModel.objects.create)(
                        **song_data
                    )
            else:
                # Create new song
                song_obj = await sync_to_async(SongModel.objects.create)(**song_data)

            return self._to_entity(song_obj)

        except Exception as e:
            self.logger.error(f"Error saving song: {str(e)}")
            raise

    async def get_by_id(self, song_id: str) -> Optional[SongEntity]:
        """Obtiene una canción por ID"""
        try:
            song = await sync_to_async(SongModel.objects.get)(
                id=song_id, is_active=True
            )
            return self._to_entity(song)
        except SongModel.DoesNotExist:
            return None
        except Exception as e:
            self.logger.error(f"Error getting song by id {song_id}: {str(e)}")
            return None

    async def get_by_source(
        self, source_type: str, source_id: str
    ) -> Optional[SongEntity]:
        """Obtiene una canción por fuente y ID de fuente"""
        try:
            song = await sync_to_async(SongModel.objects.get)(
                source_type=source_type, source_id=source_id, is_active=True
            )
            return self._to_entity(song)
        except SongModel.DoesNotExist:
            return None
        except Exception as e:
            self.logger.error(
                f"Error getting song by source {source_type}:{source_id}: {str(e)}"
            )
            return None

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[SongEntity]:
        """Obtiene todas las canciones activas"""
        try:
            songs = await sync_to_async(list)(
                SongModel.objects.filter(is_active=True).order_by("-created_at")[
                    offset : offset + limit
                ]
            )
            return [self._to_entity(song) for song in songs]
        except Exception as e:
            self.logger.error(f"Error getting all songs: {str(e)}")
            return []

    async def get_random(self, limit: int = 6) -> List[SongEntity]:
        """Obtiene canciones aleatorias"""
        try:
            songs = await sync_to_async(list)(
                SongModel.objects.filter(is_active=True).order_by("?")[:limit]
            )
            return [self._to_entity(song) for song in songs]
        except Exception as e:
            self.logger.error(f"Error getting random songs: {str(e)}")
            return []

    async def search(self, query: str, limit: int = 20) -> List[SongEntity]:
        """Busca canciones por título o artista"""
        try:
            songs = await sync_to_async(list)(
                SongModel.objects.filter(
                    Q(title__icontains=query)
                    | Q(artist_name__icontains=query)
                    | Q(album_title__icontains=query),
                    is_active=True,
                ).order_by("-play_count", "-created_at")[:limit]
            )
            return [self._to_entity(song) for song in songs]
        except Exception as e:
            self.logger.error(f"Error searching songs with query '{query}': {str(e)}")
            return []

    async def get_by_artist(
        self, artist_name: str, limit: int = 20
    ) -> List[SongEntity]:
        """Obtiene canciones por artista"""
        try:
            songs = await sync_to_async(list)(
                SongModel.objects.filter(
                    artist_name__iexact=artist_name, is_active=True
                ).order_by("-play_count", "album_title", "track_number")[:limit]
            )
            return [self._to_entity(song) for song in songs]
        except Exception as e:
            self.logger.error(
                f"Error getting songs by artist '{artist_name}': {str(e)}"
            )
            return []

    async def get_by_album(self, album_title: str, limit: int = 20) -> List[SongEntity]:
        """Obtiene canciones por álbum"""
        try:
            songs = await sync_to_async(list)(
                SongModel.objects.filter(
                    album_title__iexact=album_title, is_active=True
                ).order_by("track_number", "title")[:limit]
            )
            return [self._to_entity(song) for song in songs]
        except Exception as e:
            self.logger.error(f"Error getting songs by album '{album_title}': {str(e)}")
            return []

    async def get_most_played(self, limit: int = 10) -> List[SongEntity]:
        """Obtiene las canciones más reproducidas"""
        try:
            songs = await sync_to_async(list)(
                SongModel.objects.filter(is_active=True).order_by(
                    "-play_count", "-created_at"
                )[:limit]
            )
            return [self._to_entity(song) for song in songs]
        except Exception as e:
            self.logger.error(f"Error getting most played songs: {str(e)}")
            return []

    async def get_most_favorited(self, limit: int = 10) -> List[SongEntity]:
        """Obtiene las canciones más agregadas a favoritos"""
        try:
            songs = await sync_to_async(list)(
                SongModel.objects.filter(is_active=True).order_by(
                    "-favorite_count", "-created_at"
                )[:limit]
            )
            return [self._to_entity(song) for song in songs]
        except Exception as e:
            self.logger.error(f"Error getting most favorited songs: {str(e)}")
            return []

    async def get_recently_played(self, limit: int = 20) -> List[SongEntity]:
        """Obtiene las canciones reproducidas recientemente"""
        try:
            songs = await sync_to_async(list)(
                SongModel.objects.filter(
                    is_active=True, last_played_at__isnull=False
                ).order_by("-last_played_at")[:limit]
            )
            return [self._to_entity(song) for song in songs]
        except Exception as e:
            self.logger.error(f"Error getting recently played songs: {str(e)}")
            return []

    async def get_trending_artists(self, limit: int = 10) -> List[dict]:
        """Obtiene los artistas más populares basado en reproducciones"""
        try:
            result = await sync_to_async(list)(
                SongModel.objects.filter(is_active=True, artist_name__isnull=False)
                .values("artist_name")
                .annotate(
                    total_plays=Sum("play_count"),
                    total_songs=Count("id"),
                    total_favorites=Sum("favorite_count"),
                )
                .order_by("-total_plays")[:limit]
            )
            return result
        except Exception as e:
            self.logger.error(f"Error getting trending artists: {str(e)}")
            return []

    async def get_trending_albums(self, limit: int = 10) -> List[dict]:
        """Obtiene los álbumes más populares basado en reproducciones"""
        try:
            result = await sync_to_async(list)(
                SongModel.objects.filter(is_active=True, album_title__isnull=False)
                .values("album_title", "artist_name")
                .annotate(
                    total_plays=Sum("play_count"),
                    total_songs=Count("id"),
                    total_favorites=Sum("favorite_count"),
                )
                .order_by("-total_plays")[:limit]
            )
            return result
        except Exception as e:
            self.logger.error(f"Error getting trending albums: {str(e)}")
            return []

    async def increment_play_count(self, song_id: str) -> bool:
        """Incrementa el contador de reproducciones"""
        try:
            from django.utils import timezone

            rows_updated = await sync_to_async(
                SongModel.objects.filter(id=song_id, is_active=True).update
            )(play_count=models.F("play_count") + 1, last_played_at=timezone.now())
            return rows_updated > 0
        except Exception as e:
            self.logger.error(
                f"Error incrementing play count for song {song_id}: {str(e)}"
            )
            return False

    async def increment_favorite_count(self, song_id: str) -> bool:
        """Incrementa el contador de favoritos"""
        try:
            rows_updated = await sync_to_async(
                SongModel.objects.filter(id=song_id, is_active=True).update
            )(favorite_count=models.F("favorite_count") + 1)
            return rows_updated > 0
        except Exception as e:
            self.logger.error(
                f"Error incrementing favorite count for song {song_id}: {str(e)}"
            )
            return False

    async def increment_download_count(self, song_id: str) -> bool:
        """Incrementa el contador de descargas"""
        try:
            rows_updated = await sync_to_async(
                SongModel.objects.filter(id=song_id, is_active=True).update
            )(download_count=models.F("download_count") + 1)
            return rows_updated > 0
        except Exception as e:
            self.logger.error(
                f"Error incrementing download count for song {song_id}: {str(e)}"
            )
            return False

    async def delete(self, song_id: str) -> bool:
        """Elimina una canción (soft delete)"""
        try:
            rows_updated = await sync_to_async(
                SongModel.objects.filter(id=song_id).update
            )(is_active=False)
            return rows_updated > 0
        except Exception as e:
            self.logger.error(f"Error deleting song {song_id}: {str(e)}")
            return False

    async def exists_by_source(self, source_type: str, source_id: str) -> bool:
        """Verifica si existe una canción con la fuente específica"""
        try:
            return await sync_to_async(
                SongModel.objects.filter(
                    source_type=source_type, source_id=source_id, is_active=True
                ).exists
            )()
        except Exception as e:
            self.logger.error(
                f"Error checking existence for source {source_type}:{source_id}: {str(e)}"
            )
            return False

    def _to_entity(self, song_model: SongModel) -> SongEntity:
        """Convierte un modelo de Django a una entidad"""
        return SongEntity(
            id=str(song_model.id),
            title=song_model.title,
            album_id=str(song_model.album_id) if song_model.album_id else None,
            artist_id=str(song_model.artist_id) if song_model.artist_id else None,
            genre_id=str(song_model.genre_id) if song_model.genre_id else None,
            album_title=song_model.album_title,
            artist_name=song_model.artist_name,
            genre_name=song_model.genre_name,
            duration_seconds=song_model.duration_seconds,
            track_number=song_model.track_number,
            file_url=song_model.file_url,
            thumbnail_url=song_model.thumbnail_url,
            lyrics=song_model.lyrics,
            tags=song_model.tags,
            play_count=song_model.play_count,
            favorite_count=song_model.favorite_count,
            download_count=song_model.download_count,
            source_type=song_model.source_type,
            source_id=song_model.source_id,
            source_url=song_model.source_url,
            is_explicit=song_model.is_explicit,
            is_active=song_model.is_active,
            is_premium=song_model.is_premium,
            audio_quality=song_model.audio_quality,
            created_at=song_model.created_at,
            updated_at=song_model.updated_at,
            last_played_at=song_model.last_played_at,
            release_date=song_model.release_date,
        )
