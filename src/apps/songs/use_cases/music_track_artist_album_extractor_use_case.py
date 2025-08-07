import re
from typing import Dict, Optional

from common.interfaces.ibase_use_case import BaseUseCase
from common.types.media_types import MusicTrackData
from common.utils.logging_decorators import log_execution, log_performance

from ...albums.domain.repository import IAlbumRepository
from ...albums.use_cases.save_album_use_case import SaveAlbumUseCase
from ...artists.domain.repository import IArtistRepository
from ...artists.use_cases.save_artist_use_case import SaveArtistUseCase


class MusicTrackArtistAlbumExtractorUseCase(BaseUseCase[MusicTrackData, Dict]):
    """Caso de uso para extraer y guardar información de artistas y álbumes desde tracks de música"""

    def __init__(
        self, artist_repository: IArtistRepository, album_repository: IAlbumRepository
    ):
        super().__init__()
        self.artist_repository = artist_repository
        self.album_repository = album_repository

        # Casos de uso para guardar
        self.save_artist_use_case = SaveArtistUseCase(artist_repository)
        self.save_album_use_case = SaveAlbumUseCase(album_repository)

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)  # Reduced threshold for better monitoring
    def execute(self, track: MusicTrackData) -> Dict:
        """
        Extrae y guarda información de artista y álbum desde un track de música

        Args:
            track: Datos del track de música

        Returns:
            Diccionario con IDs del artista y álbum guardados
            {
                "artist_id": str,
                "album_id": str (opcional),
                "artist_name": str,
                "album_title": str (opcional)
            }
        """
        result = {
            "artist_id": None,
            "album_id": None,
            "artist_name": None,
            "album_title": None,
        }

        try:
            # Early validation
            if not track or not track.title:
                self.logger.warning("Invalid track data provided")
                return result

            # 1. Extraer y procesar información del artista
            try:
                artist_info = self._extract_artist_info(track)
                if artist_info:
                    saved_artist = self.save_artist_use_case.execute(artist_info)
                    if saved_artist:
                        result["artist_id"] = saved_artist.id
                        result["artist_name"] = saved_artist.name
                        self.logger.info(
                            f"✅ Artist processed: {saved_artist.name} (ID: {saved_artist.id})"
                        )
                    else:
                        self.logger.warning(
                            f"⚠️  Failed to save artist: {artist_info.get('name', 'Unknown')}"
                        )
                else:
                    self.logger.info("No artist information found in track")
            except Exception as e:
                self.logger.warning(f"Artist processing failed: {str(e)}")

            # 2. Extraer y procesar información del álbum (solo si hay artista y título de álbum)
            if result["artist_id"] and result["artist_name"] and track.album_title:
                try:
                    album_info = self._extract_album_info(
                        track, result["artist_id"], result["artist_name"]
                    )
                    if album_info:
                        saved_album = self.save_album_use_case.execute(album_info)
                        if saved_album:
                            result["album_id"] = saved_album.id
                            result["album_title"] = saved_album.title
                            self.logger.info(
                                f"✅ Album processed: {saved_album.title} (ID: {saved_album.id})"
                            )
                        else:
                            self.logger.warning(
                                f"⚠️  Failed to save album: {album_info.get('title', 'Unknown')}"
                            )
                    else:
                        self.logger.info("No valid album information extracted")
                except Exception as e:
                    self.logger.warning(f"Album processing failed: {str(e)}")
            else:
                if not result["artist_id"]:
                    self.logger.info("Skipping album processing: no artist ID")
                elif not track.album_title:
                    self.logger.info(
                        "Skipping album processing: no album title in track"
                    )

            return result

        except Exception as e:
            self.logger.error(f"Error processing track artist/album info: {str(e)}")
            return result

    def _extract_artist_info(self, track: MusicTrackData) -> Optional[Dict]:
        """
        Extrae información del artista desde el track

        Args:
            track: Datos del track

        Returns:
            Diccionario con información del artista o None
        """
        try:
            artist_name = track.artist_name
            if not artist_name:
                return None

            # Limpiar el nombre del artista
            artist_name = self._clean_artist_name(artist_name)
            if not artist_name:
                return None

            # Intentar extraer información adicional del canal de YouTube
            channel_info = self._extract_channel_info(track)

            artist_data = {
                "name": artist_name,
                "source_type": "youtube",
                "source_id": channel_info.get("channel_id") if channel_info else None,
                "source_url": channel_info.get("channel_url") if channel_info else None,
                "image_url": track.thumbnail_url,  # Usar thumbnail como imagen temporal
            }

            return artist_data

        except Exception as e:
            self.logger.warning(f"Error extracting artist info: {str(e)}")
            return None

    def _extract_album_info(
        self, track: MusicTrackData, artist_id: str, artist_name: str
    ) -> Optional[Dict]:
        """
        Extrae información del álbum desde el track

        Args:
            track: Datos del track
            artist_id: ID del artista
            artist_name: Nombre del artista

        Returns:
            Diccionario con información del álbum o None
        """
        try:
            album_title = track.album_title
            if not album_title:
                return None

            # Limpiar el título del álbum
            album_title = self._clean_album_title(album_title, track.title)
            if not album_title:
                return None

            album_data = {
                "title": album_title,
                "artist_id": artist_id,
                "artist_name": artist_name,
                "cover_image_url": track.thumbnail_url,  # Usar thumbnail como portada temporal
                "source_type": "youtube",
                "source_id": f"{track.video_id}_album",  # ID único para el álbum basado en el video
                "source_url": track.url,
            }

            return album_data

        except Exception as e:
            self.logger.warning(f"Error extracting album info: {str(e)}")
            return None

    def _extract_channel_info(self, track: MusicTrackData) -> Optional[Dict]:
        """
        Extrae información del canal de YouTube desde los tags o URL

        Args:
            track: Datos del track

        Returns:
            Diccionario con información del canal o None
        """
        try:
            # Intentar extraer channel_id de los tags si están disponibles
            if track.tags:
                for tag in track.tags:
                    if "channel" in tag.lower() or "artist" in tag.lower():
                        # Buscar patrones de channel ID en los tags
                        channel_match = re.search(r"UC[\w-]{22}", str(tag))
                        if channel_match:
                            channel_id = channel_match.group()
                            return {
                                "channel_id": channel_id,
                                "channel_url": f"https://www.youtube.com/channel/{channel_id}",
                            }

            return None

        except Exception as e:
            self.logger.debug(f"Could not extract channel info: {str(e)}")
            return None

    def _clean_artist_name(self, artist_name: str) -> str:
        """
        Limpia y normaliza el nombre del artista

        Args:
            artist_name: Nombre original del artista

        Returns:
            Nombre limpio del artista
        """
        if not artist_name:
            return ""

        # Remover caracteres especiales comunes en títulos de YouTube
        cleaned = re.sub(r"\s*[-–—]\s*Topic$", "", artist_name, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*VEVO$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*Official$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*Records$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*Music$", "", cleaned, flags=re.IGNORECASE)

        # Limpiar espacios extra
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned

    def _clean_album_title(self, album_title: str, song_title: str) -> str:
        """
        Limpia y normaliza el título del álbum

        Args:
            album_title: Título original del álbum
            song_title: Título de la canción (para evitar duplicación)

        Returns:
            Título limpio del álbum
        """
        if not album_title:
            return ""

        # Si el título del álbum es igual al de la canción, probablemente es un single
        if album_title.lower().strip() == song_title.lower().strip():
            return f"{song_title} - Single"

        # Limpiar caracteres especiales
        cleaned = re.sub(
            r"\s*[-–—]\s*(Single|EP|Album)$", "", album_title, flags=re.IGNORECASE
        )
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned
