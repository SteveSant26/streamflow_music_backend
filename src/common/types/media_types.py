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
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: int = 300  # 5 minutes
    max_filesize: Optional[int] = None  # bytes


@dataclass
class SearchOptions:
    """Opciones para búsqueda de videos"""

    max_results: int = 6
    video_category_id: str = "10"  # Música
    order: str = "relevance"  # relevance, date, rating, viewCount, title
    region_code: Optional[str] = None
    language: Optional[str] = None
    safe_search: str = "moderate"  # none, moderate, strict
    published_after: Optional[datetime] = None
    published_before: Optional[datetime] = None


@dataclass
class ServiceConfig:
    """Configuración base para servicios"""

    max_concurrent_operations: int = 3
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour


@dataclass
class YouTubeServiceConfig(ServiceConfig):
    """Configuración específica para YouTube service"""

    api_key: Optional[str] = None
    service_name: str = "youtube"
    api_version: str = "v3"
    quota_limit_per_day: int = 10000
    enable_quota_tracking: bool = True


@dataclass
class AudioServiceConfig(ServiceConfig):
    """Configuración específica para audio download service"""

    temp_dir: Optional[str] = None
    cleanup_temp_files: bool = True
    supported_formats: Optional[List[str]] = None
    default_quality: str = "192"

    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = [".mp3", ".m4a", ".webm", ".ogg", ".wav"]


@dataclass
class MusicServiceConfig(ServiceConfig):
    """Configuración específica para music service"""

    enable_audio_download: bool = True
    enable_thumbnail_processing: bool = True
    storage_bucket_audio: Optional[str] = None
    storage_bucket_images: Optional[str] = None
