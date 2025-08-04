from typing import List, Optional, Union

from common.factories.media_service_factory import MediaServiceFactory
from common.interfaces.ibase_use_case import BaseUseCase
from common.types.media_types import AudioTrackData
from common.utils.logging_decorators import log_execution, log_performance

from ...albums.infrastructure.repository.album_repository import AlbumRepository
from ...artists.infrastructure.repository.artist_repository import ArtistRepository
from ...genres.services.music_genre_analyzer import MusicGenreAnalyzer
from ...music_search.domain.interfaces import MusicTrackData
from ..domain.entities import SongEntity
from ..domain.repository import ISongRepository
from ..infrastructure.mappers.track_to_song_entity_mapper import TrackToSongEntityMapper
from .music_track_artist_album_extractor_use_case import (
    MusicTrackArtistAlbumExtractorUseCase,
)


class SaveTrackAsSongUseCase(
    BaseUseCase[Union[MusicTrackData, AudioTrackData], Optional[SongEntity]]
):
    """Caso de uso para guardar un track de música como canción"""

    def __init__(
        self,
        song_repository: ISongRepository,
    ):
        super().__init__()
        self.song_repository = song_repository

        download_service, file_service = MediaServiceFactory.create_media_services()
        self.media_download_service = download_service
        self.media_file_service = file_service

        self.mapper = TrackToSongEntityMapper()
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
            music_track = self._convert_to_music_track_data(track)

            # 1. Extraer y guardar información de artistas y álbumes PRIMERO
            self.logger.info(
                f"🎤 Processing artist and album information for: {music_track.title}"
            )
            artist_album_info = await self.artist_album_extractor.execute(music_track)

            artist_id = artist_album_info.get("artist_id")
            album_id = artist_album_info.get("album_id")
            artist_name = (
                artist_album_info.get("artist_name") or music_track.artist_name
            )
            album_title = (
                artist_album_info.get("album_title") or music_track.album_title
            )

            # 2. Descargar medios (audio y thumbnail)
            audio_bytes, thumbnail_bytes = await self._download_media(music_track)

            # 3. Subir archivos al storage
            (
                audio_file_name,
                thumbnail_file_name,
                updated_thumbnail_url,
            ) = await self.media_file_service.upload_media_files(
                audio_bytes, thumbnail_bytes, music_track.video_id
            )

            # 4. Obtener URL del archivo de audio
            file_url = await self._get_audio_file_url(audio_file_name)

            # 5. Analizar géneros automáticamente usando el título y tags
            analyzed_genres = await self._analyze_track_genres(music_track)

            # 6. Crear entidad de canción usando el mapper (ahora asíncrono)
            song_entity = await self.mapper.map(
                music_track,
                file_url=file_url,
                thumbnail_url=updated_thumbnail_url,
                analyzed_genres=analyzed_genres,
                artist_id=artist_id,  # Pasar el ID del artista
                album_id=album_id,  # Pasar el ID del álbum
            )

            # 7. Actualizar información desnormalizada para rendimiento
            if artist_name:
                song_entity.artist_name = artist_name
            if album_title:
                song_entity.album_title = album_title

            # Log para debugging - verificar que los IDs están en la entidad
            self.logger.debug(
                f"Song entity created with artist_id: {song_entity.artist_id}, album_id: {song_entity.album_id}"
            )

            self.logger.info(
                f"🎵 Created song entity '{music_track.title}' with {len(song_entity.genre_ids or [])} genre(s): {song_entity.genre_ids}"
            )
            if artist_id:
                self.logger.info(f"   🎤 Artist: {artist_name} (ID: {artist_id})")
            if album_id:
                self.logger.info(f"   💿 Album: {album_title} (ID: {album_id})")

            return await self.song_repository.save(song_entity)

        except Exception as e:
            self.logger.error(f"Error saving track as song: {str(e)}")
            return None

    async def _download_media(
        self, track: MusicTrackData
    ) -> tuple[Optional[bytes], Optional[bytes]]:
        """
        Descarga audio y thumbnail del track

        Args:
            track: Datos del track

        Returns:
            Tuple[audio_bytes, thumbnail_bytes]
        """
        audio_bytes = None
        thumbnail_bytes = None

        # Descargar audio si no existe y hay video_id
        if not track.audio_file_name and track.video_id:
            self.logger.info(f"Downloading audio for track: {track.title}")
            audio_bytes = await self.media_download_service.download_audio(
                track.video_id
            )
            if not audio_bytes:
                self.logger.warning(
                    f"Failed to download audio for track: {track.title}"
                )

        # Descargar thumbnail si existe URL
        if track.thumbnail_url:
            self.logger.info(f"Downloading thumbnail for track: {track.title}")
            thumbnail_bytes = await self.media_download_service.download_thumbnail(
                track.thumbnail_url
            )
            if not thumbnail_bytes:
                self.logger.warning(
                    f"Failed to download thumbnail for track: {track.title}"
                )

        return audio_bytes, thumbnail_bytes

    async def _get_audio_file_url(
        self, audio_file_name: Optional[str]
    ) -> Optional[str]:
        """
        Obtiene la URL del archivo de audio si existe

        Args:
            audio_file_name: Nombre del archivo de audio

        Returns:
            URL del archivo o None
        """
        if audio_file_name:
            # Acceder al storage a través del factory para obtener la URL
            from common.factories import StorageServiceFactory

            storage_service = StorageServiceFactory.create_music_files_service()
            return storage_service.get_item_url(audio_file_name)
        return None

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

    def _convert_to_music_track_data(
        self, track: Union[MusicTrackData, AudioTrackData]
    ) -> MusicTrackData:
        """
        Convierte AudioTrackData a MusicTrackData si es necesario

        Args:
            track: Track data (MusicTrackData o AudioTrackData)

        Returns:
            MusicTrackData
        """
        # Si ya es MusicTrackData, retornarlo tal como está
        if isinstance(track, MusicTrackData):
            return track

        # Si es AudioTrackData, convertirlo a MusicTrackData
        return MusicTrackData(
            video_id=track.video_id,
            title=track.title,
            artist_name=track.artist_name,
            album_title=track.album_title,
            duration_seconds=track.duration_seconds,
            thumbnail_url=track.thumbnail_url,
            genre=track.genre,
            tags=track.tags,
            url=track.url,
            audio_file_data=track.audio_file_data,
            audio_file_name=track.audio_file_name,
        )
