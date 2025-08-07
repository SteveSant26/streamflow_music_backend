import traceback
from typing import Optional

from apps.songs.domain.repository.Isong_repository import ISongRepository
from common.mixins.logging_mixin import LoggingMixin
from common.services.lyrics_manager import LyricsManager
from src.apps.songs.domain.exceptions import SongNotFoundException


class GetSongLyricsUseCase(LoggingMixin):
    """Use case para obtener letras de una canción"""

    def __init__(self, song_repository: ISongRepository):
        super().__init__()
        self.lyrics_manager = LyricsManager()
        self.song_repository = song_repository

    async def execute(self, song_id: str) -> Optional[str]:
        """
        Obtiene las letras de una canción.
        """
        try:
            song = await self.song_repository.get_by_id(song_id)
            if not song:
                raise SongNotFoundException(f"Canción con ID {song_id} no encontrada")
            if song.lyrics:
                self.logger.debug(f"Letras encontradas en BD para: {song.title}")
                return song.lyrics
            self.logger.info(f"Buscando letras para: {song.title}")
            lyrics = await self.lyrics_manager.get_lyrics(
                title=song.title,
                artist=song.artist_name if song.artist_name else "Unknown Artist",
                youtube_id=song.source_id if song.source_type == "youtube" else None,
            )
            if lyrics:
                song.lyrics = lyrics
                await self.song_repository.save(song)
                self.logger.info(f"Letras guardadas para: {song.title}")
                return lyrics
            else:
                self.logger.warning(f"No se encontraron letras para: {song.title}")
                return None
        except SongNotFoundException:
            self.logger.error(f"Canción con ID {song_id} no encontrada")
            return None
        except Exception as e:
            traceback.print_exc()
            self.logger.error(
                f"Error obteniendo letras para canción {song_id}: {str(e)}"
            )
            return None
