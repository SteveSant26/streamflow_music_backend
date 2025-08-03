from typing import List, Optional, cast

from asgiref.sync import sync_to_async
from django.db.models import Count, Q, Sum

from apps.songs.api.mappers import SongEntityModelMapper
from common.core import BaseDjangoRepository

from ...domain.entities import SongEntity
from ...domain.repository.Isong_repository import ISongRepository
from ..models.song_model import SongModel


class SongRepository(ISongRepository, BaseDjangoRepository[SongEntity, SongModel]):
    """Implementación del repositorio de canciones usando Django ORM"""

    def __init__(self):
        super().__init__(SongModel, SongEntityModelMapper())

    async def save(self, entity: SongEntity) -> SongEntity:
        """Guarda una canción"""
        try:
            song_data = self.mapper.entity_to_model_data(entity)

            if entity.id:
                try:
                    song_obj = await self.model_class.objects.aget(id=entity.id)
                    for key, value in song_data.items():
                        setattr(song_obj, key, value)
                    await song_obj.asave()
                except SongModel.DoesNotExist:
                    self.logger.warning(
                        f"Song with ID {entity.id} not found, creating new one"
                    )
                    song_obj = await self.model_class.objects.acreate(**song_data)
            else:
                song_obj = await self.model_class.objects.acreate(**song_data)

            song_mapper = cast(SongEntityModelMapper, self.mapper)
            if entity.genre_ids:
                await song_mapper.set_entity_genres_to_model(song_obj, entity.genre_ids)
            else:
                await song_obj.genres.aclear()

            return self.mapper.model_to_entity(song_obj)

        except Exception as e:
            self.logger.error(f"Error saving song: {str(e)}")
            raise

    async def get_by_source(
        self, source_type: str, source_id: str
    ) -> Optional[SongEntity]:
        """Obtiene una canción por fuente y ID de fuente"""
        try:
            song = await self.model_class.objects.aget(
                source_type=source_type,
                source_id=source_id,
            )
            return self.mapper.model_to_entity(song)
        except SongModel.DoesNotExist:
            return None
        except Exception as e:
            self.logger.error(
                f"Error getting song by source {source_type}:{source_id}: {str(e)}"
            )
            return None

    async def get_random(self, limit: int = 6) -> List[SongEntity]:
        """Obtiene canciones aleatorias"""
        try:
            songs = await sync_to_async(
                lambda: list(SongModel.objects.all().order_by("?")[:limit])
            )()
            return self.mapper.models_to_entities(songs)
        except Exception as e:
            self.logger.error(f"Error getting random songs: {str(e)}")
            return []

    async def search(self, query: str, limit: int = 20) -> List[SongEntity]:
        """Busca canciones por título o artista"""
        try:
            songs = await sync_to_async(
                lambda: list(
                    SongModel.objects.filter(
                        Q(title__icontains=query)
                        | Q(artist_name__icontains=query)
                        | Q(album_title__icontains=query),
                    ).order_by("-play_count", "-created_at")[:limit]
                )
            )()
            return self.mapper.models_to_entities(songs)
        except Exception as e:
            self.logger.error(f"Error searching songs with query '{query}': {str(e)}")
            return []

    async def get_by_artist(
        self, artist_name: str, limit: int = 20
    ) -> List[SongEntity]:
        """Obtiene canciones por artista"""
        try:
            songs = await sync_to_async(
                lambda: list(
                    SongModel.objects.filter(
                        artist_name__iexact=artist_name,
                    ).order_by(
                        "-play_count", "album_title", "track_number"
                    )[:limit]
                )
            )()
            return self.mapper.models_to_entities(songs)
        except Exception as e:
            self.logger.error(
                f"Error getting songs by artist '{artist_name}': {str(e)}"
            )
            return []

    async def get_by_album(self, album_title: str, limit: int = 20) -> List[SongEntity]:
        """Obtiene canciones por álbum"""
        try:
            songs = await sync_to_async(
                lambda: list(
                    SongModel.objects.filter(
                        album_title__iexact=album_title,
                    ).order_by(
                        "track_number", "title"
                    )[:limit]
                )
            )()
            return self.mapper.models_to_entities(songs)
        except Exception as e:
            self.logger.error(f"Error getting songs by album '{album_title}': {str(e)}")
            return []

    async def get_most_played(self, limit: int = 10) -> List[SongEntity]:
        """Obtiene las canciones más reproducidas"""
        try:
            songs = await sync_to_async(
                lambda: list(
                    SongModel.objects.all().order_by("-play_count", "-created_at")[
                        :limit
                    ]
                )
            )()
            return self.mapper.models_to_entities(songs)
        except Exception as e:
            self.logger.error(f"Error getting most played songs: {str(e)}")
            return []

    async def get_most_favorited(self, limit: int = 10) -> List[SongEntity]:
        """Obtiene las canciones más agregadas a favoritos"""
        try:
            songs = await sync_to_async(
                lambda: list(
                    SongModel.objects.all().order_by("-favorite_count", "-created_at")[
                        :limit
                    ]
                )
            )()
            return self.mapper.models_to_entities(songs)
        except Exception as e:
            self.logger.error(f"Error getting most favorited songs: {str(e)}")
            return []

    async def get_recently_played(self, limit: int = 20) -> List[SongEntity]:
        """Obtiene las canciones reproducidas recientemente"""
        try:
            songs = await sync_to_async(
                lambda: list(
                    SongModel.objects.filter(last_played_at__isnull=False).order_by(
                        "-last_played_at"
                    )[:limit]
                )
            )()
            return self.mapper.models_to_entities(songs)
        except Exception as e:
            self.logger.error(f"Error getting recently played songs: {str(e)}")
            return []

    async def get_trending_artists(self, limit: int = 10) -> List[dict]:
        """Obtiene los artistas más populares basado en reproducciones"""
        try:
            result = await sync_to_async(
                lambda: list(
                    SongModel.objects.filter(artist_name__isnull=False)
                    .values("artist_name")
                    .annotate(
                        total_plays=Sum("play_count"),
                        total_songs=Count("id"),
                        total_favorites=Sum("favorite_count"),
                    )
                    .order_by("-total_plays")[:limit]
                )
            )()
            return result
        except Exception as e:
            self.logger.error(f"Error getting trending artists: {str(e)}")
            return []

    async def get_trending_albums(self, limit: int = 10) -> List[dict]:
        """Obtiene los álbumes más populares basado en reproducciones"""
        try:
            result = await sync_to_async(
                lambda: list(
                    SongModel.objects.filter(album_title__isnull=False)
                    .values("album_title", "artist_name")
                    .annotate(
                        total_plays=Sum("play_count"),
                        total_songs=Count("id"),
                        total_favorites=Sum("favorite_count"),
                    )
                    .order_by("-total_plays")[:limit]
                )
            )()
            return result
        except Exception as e:
            self.logger.error(f"Error getting trending albums: {str(e)}")
            return []

    async def increment_play_count(self, song_id: str) -> bool:
        """Incrementa el contador de reproducciones"""
        try:
            song = await self.model_class.objects.aget(
                id=song_id,
            )
            await song.increment_play_count()
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
            song = await self.model_class.objects.aget(
                id=song_id,
            )
            await song.increment_favorite_count()
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
            song = await self.model_class.objects.aget(
                id=song_id,
            )
            await song.increment_download_count()
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
            return await SongModel.objects.filter(
                source_type=source_type,
                source_id=source_id,
            ).aexists()
        except Exception as e:
            self.logger.error(
                f"Error checking existence for source {source_type}:{source_id}: {str(e)}"
            )
            return False
