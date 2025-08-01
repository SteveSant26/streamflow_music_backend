"""
Tipos de datos para medios (música, video, etc.)
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


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
    """Información específica de un video de YouTube"""


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


@dataclass
class MusicTrackData(AudioTrackData):
    """Datos específicos de una pista musical"""


@dataclass
class DownloadOptions:
    """Opciones para la descarga de audio"""

    format: str = "bestaudio/best"
    extract_audio: bool = True
    audio_format: str = "mp3"
    audio_quality: str = "192"
    quiet: bool = True
    no_warnings: bool = True


@dataclass
class SearchOptions:
    """Opciones para búsqueda de videos"""

    max_results: int = 6
    video_category_id: str = "10"  # Música
    order: str = "relevance"  # relevance, date, rating, viewCount, title
    region_code: Optional[str] = None
    language: Optional[str] = None
