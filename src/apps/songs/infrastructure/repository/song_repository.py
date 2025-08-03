from typing import List, Optional

from asgiref.sync import sync_to_async
from django.db.models import Count, Q, Sum

from apps.songs.api.mappers import SongEntityModelMapper
from common.core import BaseDjangoRepository

from ...domain.entities import SongEntity
from ...domain.repository.Isong_repository import ISongRepository
from ..models.song_model import SongModel


class SongRepository(BaseDjangoRepository[SongEntity, SongModel], ISongRepository):
    """Implementación del repositorio de canciones usando Django ORM"""

    def __init__(self):
        song_mapper = SongEntityModelMapper()
        super().__init__(SongModel, song_mapper)
        # Declarar el tipo específico del mapper para acceder a métodos especializados
        self.mapper: SongEntityModelMapper = song_mapper

    async def save(self, entity: SongEntity) -> SongEntity:
        """Guarda una canción"""
        try:
            song_data = self.mapper.entity_to_model_data(entity)

            if entity.id:
                # Update existing song - first check if it exists
                try:
                    song_obj = await sync_to_async(SongModel.objects.get)(id=entity.id)
                    for key, value in song_data.items():
                        setattr(song_obj, key, value)
                    await sync_to_async(song_obj.save)()

                    # Actualizar los géneros (many-to-many)
                    if entity.genre_ids:
                        await self.mapper.set_entity_genres_to_model(
                            song_obj, entity.genre_ids
                        )
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
                        await self.mapper.set_entity_genres_to_model(
                            song_obj, entity.genre_ids
                        )
            else:
                # Create new song
                song_obj = await sync_to_async(SongModel.objects.create)(**song_data)
                # Asignar géneros para nueva canción
                if entity.genre_ids:
                    await self.mapper.set_entity_genres_to_model(
                        song_obj, entity.genre_ids
                    )

            return self._model_to_entity(song_obj)

        except Exception as e:
            self.logger.error(f"Error saving song: {str(e)}")
            raise

    # get_by_id ya está implementado en BaseReadOnlyDjangoRepository

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

    async def get_all_paginated(
        self, limit: int = 100, offset: int = 0
    ) -> List[SongEntity]:
        """Obtiene todas las canciones activas con paginación"""
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
            song = await sync_to_async(SongModel.objects.get)(
                id=song_id, is_active=True
            )
            await sync_to_async(song.increment_play_count)()
            return True
        except SongModel.DoesNotExist:
            self.logger.warning(f"Song with id {song_id} not found")
            return False
        except Exception as e:
            self.logger.error(
                f"Error incrementing play count for song {song_id}: {str(e)}"
            )
            return False

    async def increment_favorite_count(self, song_id: str) -> bool:
        """Incrementa el contador de favoritos"""
        try:
            song = await sync_to_async(SongModel.objects.get)(
                id=song_id, is_active=True
            )
            await sync_to_async(song.increment_favorite_count)()
            return True
        except SongModel.DoesNotExist:
            self.logger.warning(f"Song with id {song_id} not found")
            return False
        except Exception as e:
            self.logger.error(
                f"Error incrementing favorite count for song {song_id}: {str(e)}"
            )
            return False

    async def increment_download_count(self, song_id: str) -> bool:
        """Incrementa el contador de descargas"""
        try:
            song = await sync_to_async(SongModel.objects.get)(
                id=song_id, is_active=True
            )
            await sync_to_async(song.increment_download_count)()
            return True
        except SongModel.DoesNotExist:
            self.logger.warning(f"Song with id {song_id} not found")
            return False
        except Exception as e:
            self.logger.error(
                f"Error incrementing download count for song {song_id}: {str(e)}"
            )
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
        return self.mapper.model_to_entity(model)

    def _entity_to_model(self, entity: SongEntity) -> dict:
        """Convierte una entidad a datos del modelo"""
        return self.mapper.entity_to_model_data(entity)
