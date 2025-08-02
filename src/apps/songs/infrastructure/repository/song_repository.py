from typing import List, Optional

from asgiref.sync import sync_to_async
from django.db import models
from django.db.models import Count, Q, Sum

from common.core import BaseDjangoRepository

from ...domain.entities import SongEntity
from ...domain.repository.Isong_repository import ISongRepository
from ..models.song_model import SongModel


class SongRepository(BaseDjangoRepository[SongEntity, SongModel], ISongRepository):
    """Implementación del repositorio de canciones usando Django ORM"""

    def __init__(self):
        super().__init__(SongModel)

    async def save(self, entity: SongEntity) -> SongEntity:
        """Guarda una canción"""
        try:
            song_data = {
                "title": entity.title,
                "album_id": entity.album_id,
                "artist_id": entity.artist_id,
                "album_title": entity.album_title,
                "artist_name": entity.artist_name,
                "genre_names": entity.genre_names or [],
                "duration_seconds": entity.duration_seconds,
                "track_number": entity.track_number,
                "file_url": entity.file_url,
                "thumbnail_url": entity.thumbnail_url,
                "lyrics": entity.lyrics,
                "play_count": entity.play_count,
                "favorite_count": entity.favorite_count,
                "download_count": entity.download_count,
                "source_type": entity.source_type,
                "source_id": entity.source_id,
                "source_url": entity.source_url,
                "is_explicit": entity.is_explicit,
                "is_active": entity.is_active,
                "is_premium": entity.is_premium,
                "audio_quality": entity.audio_quality,
                "last_played_at": entity.last_played_at,
                "release_date": entity.release_date,
            }

            if entity.id:
                # Update existing song - first check if it exists
                try:
                    song_obj = await sync_to_async(SongModel.objects.get)(id=entity.id)
                    for key, value in song_data.items():
                        setattr(song_obj, key, value)
                    await sync_to_async(song_obj.save)()

                    # Actualizar los géneros (many-to-many)
                    if entity.genre_ids:
                        from apps.genres.infrastructure.models.genre_model import (
                            GenreModel,
                        )

                        genre_objects = await sync_to_async(list)(
                            GenreModel.objects.filter(id__in=entity.genre_ids)
                        )
                        await sync_to_async(song_obj.genres.set)(genre_objects)
                    else:
                        await sync_to_async(song_obj.genres.clear)()

                except SongModel.DoesNotExist:
                    # Song doesn't exist, create it instead
                    self.logger.warning(
                        f"Song with ID {entity.id} not found, creating new one"
                    )
                    song_obj = await sync_to_async(SongModel.objects.create)(
                        **song_data
                    )
                    # Asignar géneros para nueva canción
                    if entity.genre_ids:
                        from apps.genres.infrastructure.models.genre_model import (
                            GenreModel,
                        )

                        genre_objects = await sync_to_async(list)(
                            GenreModel.objects.filter(id__in=entity.genre_ids)
                        )
                        await sync_to_async(song_obj.genres.set)(genre_objects)
            else:
                # Create new song
                song_obj = await sync_to_async(SongModel.objects.create)(**song_data)
                # Asignar géneros para nueva canción
                if entity.genre_ids:
                    from apps.genres.infrastructure.models.genre_model import GenreModel

                    genre_objects = await sync_to_async(list)(
                        GenreModel.objects.filter(id__in=entity.genre_ids)
                    )
                    await sync_to_async(song_obj.genres.set)(genre_objects)

            return self._model_to_entity(song_obj)

        except Exception as e:
            self.logger.error(f"Error saving song: {str(e)}")
            raise

    async def get_by_id(self, entity_id: str) -> Optional[SongEntity]:
        """Obtiene una canción por ID"""
        try:
            song = await sync_to_async(SongModel.objects.get)(
                id=entity_id, is_active=True
            )
            return self._model_to_entity(song)
        except SongModel.DoesNotExist:
            return None
        except Exception as e:
            self.logger.error(f"Error getting song by id {entity_id}: {str(e)}")
            return None

    async def get_by_source(
        self, source_type: str, source_id: str
    ) -> Optional[SongEntity]:
        """Obtiene una canción por fuente y ID de fuente"""
        try:
            song = await sync_to_async(SongModel.objects.get)(
                source_type=source_type, source_id=source_id, is_active=True
            )
            return self._model_to_entity(song)
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
            return [self._model_to_entity(song) for song in songs]
        except Exception as e:
            self.logger.error(f"Error getting all songs: {str(e)}")
            return []

    async def get_random(self, limit: int = 6) -> List[SongEntity]:
        """Obtiene canciones aleatorias"""
        try:
            songs = await sync_to_async(list)(
                SongModel.objects.filter(is_active=True).order_by("?")[:limit]
            )
            return [self._model_to_entity(song) for song in songs]
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
            return [self._model_to_entity(song) for song in songs]
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
            return [self._model_to_entity(song) for song in songs]
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
            return [self._model_to_entity(song) for song in songs]
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
            return [self._model_to_entity(song) for song in songs]
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
            return [self._model_to_entity(song) for song in songs]
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
            return [self._model_to_entity(song) for song in songs]
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

    async def delete(self, entity_id: str) -> bool:
        """Elimina una canción (soft delete)"""
        try:
            rows_updated = await sync_to_async(
                SongModel.objects.filter(id=entity_id).update
            )(is_active=False)
            return rows_updated > 0
        except Exception as e:
            self.logger.error(f"Error deleting song {entity_id}: {str(e)}")
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

    def _model_to_entity(self, model: SongModel) -> SongEntity:
        """Convierte un modelo de Django a una entidad"""
        return SongEntity(
            id=str(model.id),
            title=model.title,
            album_id=str(model.album_id) if model.album_id else None,
            artist_id=str(model.artist_id) if model.artist_id else None,
            genre_ids=[],  # Se puede cargar por separado si es necesario
            album_title=model.album_title,
            artist_name=model.artist_name,
            genre_names=model.genre_names if model.genre_names else [],
            duration_seconds=model.duration_seconds,
            track_number=model.track_number,
            file_url=model.file_url,
            thumbnail_url=model.thumbnail_url,
            lyrics=model.lyrics,
            play_count=model.play_count,
            favorite_count=model.favorite_count,
            download_count=model.download_count,
            source_type=model.source_type,
            source_id=model.source_id,
            source_url=model.source_url,
            is_explicit=model.is_explicit,
            is_active=model.is_active,
            is_premium=model.is_premium,
            audio_quality=model.audio_quality,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_played_at=model.last_played_at,
            release_date=model.release_date,
        )
