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

# Importar los nuevos módulos
from .processors.media_processor import MediaProcessor
from .processors.song_entity_processor import SongEntityProcessor
from .services.song_database_service import SongDatabaseService


class SaveTrackAsSongUseCase(
    BaseUseCase[Union[MusicTrackData, AudioTrackData], Optional[SongEntity]]
):
    """Caso de uso para guardar un track de música como canción"""

    def __init__(
        self,
        song_repository: ISongRepository,
    ):
        super().__init__()

        # Inicializar servicios modulares
        self.media_processor = MediaProcessor()
        self.song_entity_processor = SongEntityProcessor()
        self.database_service = SongDatabaseService(song_repository)
        self.data_converter = MusicDataConverter()

        # Servicios específicos que se mantienen aquí
        self.genre_analyzer = MusicGenreAnalyzer()

        # Repositorios para artistas y álbumes
        self.artist_repository = ArtistRepository()
        self.album_repository = AlbumRepository()

        # Extractor para procesar información de artistas y álbumes
        self.artist_album_extractor = MusicTrackArtistAlbumExtractorUseCase(
            self.artist_repository, self.album_repository
        )

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(
        threshold_seconds=4.0
    )  # Operación de guardado y procesamiento de archivos
    async def execute(
        self, track: Union[MusicTrackData, AudioTrackData]
    ) -> Optional[SongEntity]:
        """
        Convierte un MusicTrackData o AudioTrackData en SongEntity y lo guarda

        Args:
            track: Datos del track de música (MusicTrackData o AudioTrackData)

        Returns:
            Entidad de canción guardada o None si falla
        """
        try:
            # Convertir AudioTrackData a MusicTrackData si es necesario
            music_track = self.data_converter.convert_to_music_track_data(track)

            # 1. Procesar información de artistas y álbumes
            artist_album_info = await self._process_artist_album_info(music_track)

            # 2. Procesar archivos multimedia y storage
            media_result = await self.media_processor.process_media_files(music_track)
            if not media_result:
                return None

            file_url, updated_thumbnail_url = media_result

            # 3. Analizar géneros y crear entidad
            analyzed_genres = await self._analyze_track_genres(music_track)
            song_entity = await self.song_entity_processor.create_song_entity(
                music_track,
                file_url,
                updated_thumbnail_url,
                analyzed_genres,
                artist_album_info,
            )

            # 4. Guardar en base de datos
            return await self.database_service.save_song_to_database(
                song_entity, music_track.title
            )

        except Exception as e:
            self.logger.error(f"Error saving track as song: {str(e)}")
            return None

    async def _process_artist_album_info(self, music_track: MusicTrackData) -> dict:
        """
        Procesa información de artistas y álbumes

        Args:
            music_track: Datos del track de música

        Returns:
            Diccionario con información de artista y álbum
        """
        self.logger.info(
            f"🎤 Processing artist and album information for: {music_track.title}"
        )
        return await self.artist_album_extractor.execute(music_track)

    async def _analyze_track_genres(self, track: MusicTrackData) -> List[str]:
        """
        Analiza automáticamente los géneros de un track basándose en título y tags

        Args:
            track: Datos del track de música

        Returns:
            Lista de nombres de géneros detectados
        """
        try:
            self.logger.debug(f"Starting genre analysis for: {track.title}")
            self.logger.debug(f"Artist: {track.artist_name}")
            self.logger.debug(f"Original genre: {track.genre}")
            self.logger.debug(f"Available tags: {track.tags}")

            # Usar el analizador de géneros para extraer géneros automáticamente
            # usando los metadatos disponibles del track
            genre_matches = await self.genre_analyzer.analyze_music_from_metadata(
                title=track.title,
                artist=track.artist_name,
                album=track.album_title or "",
                tags=track.tags,  # Los tags de YouTube que contienen información valiosa
                max_genres=3,  # Máximo 3 géneros
                min_confidence=0.1,  # Reducido para ser más inclusivo
            )

            # Extraer solo los nombres de los géneros
            detected_genres = [match.genre.name for match in genre_matches]

            if detected_genres:
                self.logger.info(
                    f"✅ Detected genres for '{track.title}': {detected_genres}"
                )
                # Log detalles de los matches para debug
                for match in genre_matches:
                    self.logger.debug(
                        f"  • {match.genre.name} (confidence: {match.confidence_score:.3f}, "
                        f"source: {match.source}, indicators: {match.matching_indicators})"
                    )
            else:
                self.logger.warning(
                    f"❌ No genres detected for '{track.title}' using title and {len(track.tags)} tags. "
                    f"Will use original genre: {track.genre}"
                )
                # Log algunos tags para debug si hay
                if track.tags:
                    self.logger.debug(
                        f"Available tags were: {track.tags[:10]}..."
                    )  # Primeros 10 tags

            return detected_genres

        except Exception as e:
            self.logger.error(
                f"Error analyzing genres for track '{track.title}': {str(e)}"
            )
            # En caso de error, retornar el género original si existe
            return [track.genre] if track.genre else []
