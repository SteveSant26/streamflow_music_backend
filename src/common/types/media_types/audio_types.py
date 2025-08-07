from dataclasses import dataclass
from typing import List, Optional

from .extraction_types import ExtractedAlbumInfo, ExtractedArtistInfo


@dataclass
class AudioTrackData:
    """Datos procesados de una pista de audio"""

    video_id: str
    title: str
    artist_name: str
    album_title: Optional[str]
    duration_seconds: int
    thumbnail_url: str
    genre: str
    tags: List[str]
    url: str
    audio_file_data: Optional[bytes] = None
    audio_file_name: Optional[str] = None
    extracted_artists: Optional[List[ExtractedArtistInfo]] = None
    extracted_albums: Optional[List[ExtractedAlbumInfo]] = None

    def __post_init__(self):
        if self.extracted_artists is None:
            self.extracted_artists = []
        if self.extracted_albums is None:
            self.extracted_albums = []


@dataclass
class MusicTrackData(AudioTrackData):
    """Datos específicos de una pista musical"""
