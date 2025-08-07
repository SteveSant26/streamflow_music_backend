from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance
from common.utils.performance_cache import youtube_search_cache
from common.utils.performance_monitor import performance_monitor
from src.common.factories.unified_music_service_factory import get_music_service

from ..api.dtos import SongSearchRequestDTO
from ..domain.entities import SongEntity
from ..domain.repository import ISongRepository


class SearchSongsUseCase(BaseUseCase[SongSearchRequestDTO, List[SongEntity]]):
    """Caso de uso para buscar canciones"""

    def __init__(self, song_repository: ISongRepository, music_service=None):
        super().__init__()
        self.song_repository = song_repository
        self.music_service = get_music_service()
        # Simple cache to avoid reprocessing same tracks in the same session
        self._processing_cache: set[str] = set()

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=3.0)  # Búsqueda puede incluir consultas externas
    def execute(self, request_dto: SongSearchRequestDTO) -> List[SongEntity]:
        """
        Busca canciones. Primero en la BD local, luego opcionalmente en YouTube.

        Args:
            request_dto: DTO con query, limit e include_youtube

        Returns:
            Lista de canciones encontradas
        """
        # Start performance monitoring
        search_id = performance_monitor.start_search(request_dto.query, "full_search")

        try:
            # Buscar en la base de datos local
            self.logger.debug(f"Searching songs locally for: '{request_dto.query}'")
            local_songs = self.song_repository.search(
                request_dto.query, request_dto.limit
            )

            if len(local_songs) >= request_dto.limit or not request_dto.include_youtube:
                self.logger.info(
                    f"Found {len(local_songs)} songs locally for query: '{request_dto.query}'"
                )
                return local_songs

            # Buscar en YouTube para completar los resultados
            self.logger.info(
                f"Searching YouTube for additional results: '{request_dto.query}'"
            )

            # Check cache first
            cache_key = f"youtube_search:{request_dto.query}:{request_dto.limit - len(local_songs)}"
            cached_tracks = youtube_search_cache.get(cache_key)

            if cached_tracks:
                self.logger.info(
                    f"Using cached YouTube results for query: '{request_dto.query}'"
                )
                youtube_tracks = cached_tracks
            else:
                # Search YouTube if not in cache
                from common.types.media_types import SearchOptions

                options = SearchOptions(
                    max_results=request_dto.limit - len(local_songs)
                )
                youtube_tracks = self.music_service.search_and_process_audio(
                    request_dto.query, options
                )

                # Cache the results
                youtube_search_cache.set(
                    cache_key, youtube_tracks, ttl=600
                )  # 10 minutes
                self.logger.info(
                    f"Cached YouTube search results for query: '{request_dto.query}'"
                )

            # Guardar nuevas canciones encontradas
            saved_count = 0
            for track in youtube_tracks:
                try:
                    # Skip if already processed in this session
                    if track.video_id in self._processing_cache:
                        self.logger.info(
                            f"🔄 Skipping already processed video: {track.video_id}"
                        )
                        continue

                    # Add to processing cache
                    self._processing_cache.add(track.video_id)

                    existing_song = self.song_repository.get_by_source(
                        "youtube", track.video_id
                    )

                    if not existing_song:
                        from .save_track_as_song_use_case import SaveTrackAsSongUseCase

                        save_track_use_case = SaveTrackAsSongUseCase(
                            self.song_repository
                        )
                        new_song = save_track_use_case.execute(track)
                        if new_song:
                            local_songs.append(new_song)
                            saved_count += 1
                            self.logger.info(f"✅ Saved new song: {new_song.title}")
                        else:
                            self.logger.warning(
                                f"⚠️  Failed to save track: {getattr(track, 'title', 'Unknown')}"
                            )
                    else:
                        local_songs.append(existing_song)
                        self.logger.info(
                            f"🔍 Using existing song: {existing_song.title}"
                        )
                except Exception as e:
                    self.logger.error(
                        f"❌ Error processing track {getattr(track, 'video_id', 'unknown')}: {str(e)}"
                    )
                    continue

            self.logger.info(
                f"Processed {len(youtube_tracks)} YouTube tracks, saved {saved_count} new songs"
            )
            final_results = local_songs[: request_dto.limit]
            self.logger.info(
                f"Total songs found for query '{request_dto.query}': {len(final_results)}"
            )

            # End performance monitoring with success
            performance_monitor.end_search(search_id, len(final_results), True)
            return final_results

        except Exception as e:
            self.logger.error(
                f"Error searching songs with query '{request_dto.query}': {str(e)}"
            )
            # End performance monitoring with error
            performance_monitor.end_search(search_id, 0, False, str(e))
            # Return existing local results if any, otherwise empty list
            try:
                return self.song_repository.search(request_dto.query, request_dto.limit)
            except Exception:
                return []
