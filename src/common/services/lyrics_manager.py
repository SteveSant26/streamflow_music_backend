from typing import Optional

from common.adapters.lyrics.lyrics_service import LyricsService
from common.utils.lyrics_validators import validate_lyrics


class LyricsManager:
    """
    Orquesta la obtención de letras usando diferentes fuentes y aplica validaciones.
    """

    def __init__(self):
        self.lyrics_service = LyricsService()

    async def get_lyrics(
        self, title: str, artist: str, youtube_id: Optional[str] = None
    ) -> Optional[str]:
        lyrics = await self.lyrics_service.get_lyrics(title, artist, youtube_id)
        if lyrics and validate_lyrics(lyrics):
            return lyrics
        return None
