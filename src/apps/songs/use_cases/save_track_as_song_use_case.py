from typing import List, Optional, Union

from common.adapters.media.media_types import MusicTrackData
from common.interfaces.ibase_use_case import BaseUseCase
from common.types.media_types import AudioTrackData
from common.utils.logging_decorators import log_execution, log_performance

from ...albums.infrastructure.repository.album_repository import AlbumRepository
from ...artists.infrastructure.repository.artist_repository import ArtistRepository
from ...genres.services.music_genre_analyzer import MusicGenreAnalyzer
from ..domain.entities import SongEntity
from ..domain.repository import ISongRepository
from .converters.music_data_converter import MusicDataConverter
from .music_track_artist_album_extractor_use_case import (
    MusicTrackArtistAlbumExtractorUseCase,
)
from .processors.media_processor import MediaProcessor
from .processors.song_entity_processor import SongEntityProcessor
from .services.song_database_service import SongDatabaseService


class SaveTrackAsSongUseCase(
    BaseUseCase[Union[MusicTrackData, AudioTrackData], Optional[SongEntity]]
):
    """Caso de uso para guardar un track de música como canción (versión totalmente síncrona)"""

    def __init__(self, song_repository: ISongRepository):
        super().__init__()
        self.media_processor = MediaProcessor()
        self.song_entity_processor = SongEntityProcessor()
        self.database_service = SongDatabaseService(song_repository)
        self.data_converter = MusicDataConverter()
        self.genre_analyzer = MusicGenreAnalyzer()
        self.artist_repository = ArtistRepository()
        self.album_repository = AlbumRepository()
        self.artist_album_extractor = MusicTrackArtistAlbumExtractorUseCase(
            self.artist_repository, self.album_repository
        )

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=3.0)  # Reduced threshold for better monitoring
    def execute(
        self, track: Union[MusicTrackData, AudioTrackData]
    ) -> Optional[SongEntity]:
        try:
            # Early validation
            if not track:
                self.logger.warning("No track data provided")
                return None

            music_track = self.data_converter.convert_to_music_track_data(track)

            if not music_track or not music_track.title:
                self.logger.warning("Invalid music track data or missing title")
                return None

            # 1. Procesar artistas y álbumes (optimizado)
            try:
                artist_album_info = self.artist_album_extractor.execute(music_track)
            except Exception as e:
                self.logger.warning(
                    f"Failed to process artist/album info: {str(e)}, continuing with empty data"
                )
                artist_album_info = {
                    "artist_id": None,
                    "album_id": None,
                    "artist_name": None,
                    "album_title": None,
                }

            # 2. Procesar media (optimizado con timeout)
            try:
                media_result = self.media_processor.process_media_files(music_track)
                if not media_result:
                    self.logger.warning(
                        f"Failed to process media files for track: {music_track.title}"
                    )
                    return None
                file_url, updated_thumbnail_url = media_result
            except Exception as e:
                self.logger.error(
                    f"Media processing failed for track: {music_track.title}: {str(e)}"
                )
                return None

            # 3. Analizar géneros (simplified)
            try:
                analyzed_genres = self._analyze_track_genres(music_track)
            except Exception as e:
                self.logger.warning(
                    f"Genre analysis failed: {str(e)}, using empty genres"
                )
                analyzed_genres = []

            # 4. Crear entidad canción
            try:
                song_entity = self.song_entity_processor.create_song_entity(
                    music_track,
                    file_url,
                    updated_thumbnail_url,
                    analyzed_genres,
                    artist_album_info,
                )
            except Exception as e:
                self.logger.error(f"Failed to create song entity: {str(e)}")
                return None

            # 5. Guardar en la base de datos
            try:
                saved_song = self.database_service.save_song_to_database(
                    song_entity, music_track.title
                )
                if saved_song:
                    self.logger.info(f"Successfully saved song: {music_track.title}")
                return saved_song
            except Exception as e:
                self.logger.error(f"Failed to save song to database: {str(e)}")
                return None

        except Exception as e:
            self.logger.error(f"Error saving track as song: {str(e)}")
            return None

    def _analyze_track_genres(self, track: MusicTrackData) -> List[str]:
        try:
            self.logger.debug(f"Starting genre analysis for: {track.title}")
            self.logger.debug(f"Artist: {track.artist_name}")
            self.logger.debug(f"Original genre: {track.genre}")
            self.logger.debug(f"Available tags: {track.tags}")

            genre_matches = self.genre_analyzer.analyze_music_from_metadata(
                title=track.title,
                artist=track.artist_name,
                album=track.album_title or "",
                tags=track.tags,
                max_genres=3,
                min_confidence=0.1,
            )

            detected_genres = [match.genre.name for match in genre_matches]

            if detected_genres:
                self.logger.info(
                    f"✅ Detected genres for '{track.title}': {detected_genres}"
                )
                for match in genre_matches:
                    self.logger.debug(
                        f"  • {match.genre.name} (confidence: {match.confidence_score:.3f}, "
                        f"source: {match.source}, indicators: {match.matching_indicators})"
                    )
            else:
                self.logger.warning(
                    f"❌ No genres detected for '{track.title}'. Using original genre: {track.genre}"
                )
                if track.tags:
                    self.logger.debug(f"Available tags were: {track.tags[:10]}...")

            return detected_genres

        except Exception as e:
            self.logger.error(
                f"Error analyzing genres for track '{track.title}': {str(e)}"
            )
            return [track.genre] if track.genre else []
