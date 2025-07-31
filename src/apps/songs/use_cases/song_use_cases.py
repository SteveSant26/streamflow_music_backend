import uuid
from datetime import datetime
from typing import List, Optional

from common.factories import StorageServiceFactory
from common.mixins.logging_mixin import LoggingMixin

from ...music_search.domain.interfaces import MusicTrackData
from ...music_search.infrastructure.music_service import MusicService
from ..domain.entities import SongEntity
from ..domain.repository.Isong_repository import ISongRepository


class SongUseCases(LoggingMixin):
    """Casos de uso para gestión de canciones centrado en la aplicación"""

    def __init__(self, song_repository: ISongRepository):
        super().__init__()
        self.song_repository = song_repository
        self.music_service = MusicService()
        self.music_storage = StorageServiceFactory.create_music_files_service()

    async def get_random_songs(
        self, count: int = 6, force_refresh: bool = False
    ) -> List[SongEntity]:
        """
        Obtiene canciones aleatorias. Si no hay suficientes en la BD o force_refresh=True,
        busca nuevas canciones desde YouTube.
        """
        try:
            # Primero intentar obtener canciones de la base de datos
            if not force_refresh:
                existing_songs = await self.song_repository.get_random(count)
                if len(existing_songs) >= count:
                    self.logger.info(
                        f"Returning {len(existing_songs)} existing random songs"
                    )
                    return existing_songs

            # Si no hay suficientes canciones, buscar nuevas desde YouTube
            self.logger.info("Fetching new random songs from YouTube")
            new_tracks = await self.music_service.get_random_music_tracks(count)

            # Guardar las nuevas canciones en la base de datos
            saved_songs = []
            for track in new_tracks:
                existing_song = await self.song_repository.get_by_source(
                    "youtube", track.video_id
                )

                if existing_song:
                    saved_songs.append(existing_song)
                else:
                    new_song = await self._save_track_as_song(track)
                    if new_song:
                        saved_songs.append(new_song)

            # Si aún no tenemos suficientes, combinar con las existentes
            if len(saved_songs) < count:
                existing_songs = await self.song_repository.get_random(
                    count - len(saved_songs)
                )
                saved_songs.extend(existing_songs)

            return saved_songs[:count]

        except Exception as e:
            self.logger.error(f"Error getting random songs: {str(e)}")
            # En caso de error, intentar devolver canciones existentes
            return await self.song_repository.get_random(count)

    async def search_songs(
        self, query: str, limit: int = 20, include_youtube: bool = True
    ) -> List[SongEntity]:
        """
        Busca canciones. Primero en la BD local, luego opcionalmente en YouTube.
        """
        try:
            # Buscar en la base de datos local
            local_songs = await self.song_repository.search(query, limit)

            if len(local_songs) >= limit or not include_youtube:
                return local_songs

            # Buscar en YouTube para completar los resultados
            self.logger.info(f"Searching YouTube for additional results: '{query}'")
            youtube_tracks = await self.music_service.search_and_process_music(
                query, limit - len(local_songs)
            )

            # Guardar nuevas canciones encontradas
            for track in youtube_tracks:
                existing_song = await self.song_repository.get_by_source(
                    "youtube", track.video_id
                )

                if not existing_song:
                    new_song = await self._save_track_as_song(track)
                    if new_song:
                        local_songs.append(new_song)

            return local_songs[:limit]

        except Exception as e:
            self.logger.error(f"Error searching songs with query '{query}': {str(e)}")
            # Return existing local results if any, otherwise empty list
            try:
                return await self.song_repository.search(query, limit)
            except Exception:
                return []

    async def get_song_by_id(self, song_id: str) -> Optional[SongEntity]:
        """Obtiene una canción por ID"""
        return await self.song_repository.get_by_id(song_id)

    async def get_songs_by_artist(
        self, artist_name: str, limit: int = 20
    ) -> List[SongEntity]:
        """Obtiene canciones de un artista"""
        return await self.song_repository.get_by_artist(artist_name, limit)

    async def get_songs_by_album(
        self, album_title: str, limit: int = 20
    ) -> List[SongEntity]:
        """Obtiene canciones de un álbum"""
        return await self.song_repository.get_by_album(album_title, limit)

    async def get_most_played_songs(self, limit: int = 10) -> List[SongEntity]:
        """Obtiene las canciones más reproducidas en la aplicación"""
        return await self.song_repository.get_most_played(limit)

    async def get_most_favorited_songs(self, limit: int = 10) -> List[SongEntity]:
        """Obtiene las canciones más agregadas a favoritos"""
        return await self.song_repository.get_most_favorited(limit)

    async def get_recently_played_songs(self, limit: int = 20) -> List[SongEntity]:
        """Obtiene las canciones reproducidas recientemente"""
        return await self.song_repository.get_recently_played(limit)

    async def get_trending_artists(self, limit: int = 10) -> List[dict]:
        """Obtiene los artistas más populares basado en reproducciones de la app"""
        return await self.song_repository.get_trending_artists(limit)

    async def get_trending_albums(self, limit: int = 10) -> List[dict]:
        """Obtiene los álbumes más populares basado en reproducciones de la app"""
        return await self.song_repository.get_trending_albums(limit)

    async def increment_play_count(self, song_id: str) -> Optional[SongEntity]:
        """Incrementa el contador de reproducciones de una canción"""
        try:
            success = await self.song_repository.increment_play_count(song_id)
            if success:
                return await self.song_repository.get_by_id(song_id)
            return None
        except Exception as e:
            self.logger.error(
                f"Error incrementing play count for song {song_id}: {str(e)}"
            )
            return None

    async def increment_favorite_count(self, song_id: str) -> Optional[SongEntity]:
        """Incrementa el contador de favoritos de una canción"""
        try:
            success = await self.song_repository.increment_favorite_count(song_id)
            if success:
                return await self.song_repository.get_by_id(song_id)
            return None
        except Exception as e:
            self.logger.error(
                f"Error incrementing favorite count for song {song_id}: {str(e)}"
            )
            return None

    async def increment_download_count(self, song_id: str) -> Optional[SongEntity]:
        """Incrementa el contador de descargas de una canción"""
        try:
            success = await self.song_repository.increment_download_count(song_id)
            if success:
                return await self.song_repository.get_by_id(song_id)
            return None
        except Exception as e:
            self.logger.error(
                f"Error incrementing download count for song {song_id}: {str(e)}"
            )
            return None

    async def process_youtube_video(self, video_id: str) -> Optional[SongEntity]:
        """
        Procesa un video específico de YouTube y lo guarda como canción
        """
        try:
            # Verificar si ya existe
            existing_song = await self.song_repository.get_by_source(
                "youtube", video_id
            )
            if existing_song:
                return existing_song

            # Obtener información del video desde YouTube
            from ...music_search.infrastructure.services import YouTubeAPIService

            youtube_service = YouTubeAPIService()

            video_info = await youtube_service.get_video_details(video_id)
            if not video_info:
                return None

            # Procesar el video como track
            track = await self.music_service.process_video_to_track(video_info)
            if not track:
                return None

            # Guardar como canción
            return await self._save_track_as_song(track)

        except Exception as e:
            self.logger.error(f"Error processing YouTube video {video_id}: {str(e)}")
            return None

    async def _save_track_as_song(self, track: MusicTrackData) -> Optional[SongEntity]:
        """Convierte un MusicTrackData en SongEntity y lo guarda"""
        try:
            # Obtener URL del archivo de audio si existe
            file_url = None
            if track.audio_file_name:
                file_url = self.music_storage.get_item_url(track.audio_file_name)

            song_entity = SongEntity(
                id=str(uuid.uuid4()),
                title=track.title,
                artist_name=track.artist_name,
                album_title=track.album_title,
                duration_seconds=track.duration_seconds,
                file_url=file_url,
                thumbnail_url=track.thumbnail_url,
                genre_name=track.genre,
                tags=track.tags,
                source_type="youtube",
                source_id=track.video_id,
                source_url=track.url,
                is_active=True,
                audio_quality="standard",
                created_at=datetime.now(),
                release_date=datetime.now(),
            )

            return await self.song_repository.save(song_entity)

        except Exception as e:
            self.logger.error(f"Error saving track as song: {str(e)}")
            return None
