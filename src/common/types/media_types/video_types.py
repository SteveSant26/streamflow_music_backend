from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .extraction_types import ExtractedAlbumInfo, ExtractedArtistInfo


@dataclass
class VideoInfo:
    """Información detallada de un video"""

    video_id: str
    title: str
    channel_title: str
    channel_id: str
    thumbnail_url: str
    description: str
    duration_seconds: int
    published_at: datetime
    view_count: int
    like_count: int
    tags: List[str]
    category_id: str
    genre: str
    url: str


@dataclass
class YouTubeVideoInfo(VideoInfo):
    """Información específica de un video de YouTube con datos extraídos"""

    extracted_artists: Optional[List[ExtractedArtistInfo]] = None
    extracted_albums: Optional[List[ExtractedAlbumInfo]] = None

    def __post_init__(self):
        if self.extracted_artists is None:
            self.extracted_artists = []
        if self.extracted_albums is None:
            self.extracted_albums = []
