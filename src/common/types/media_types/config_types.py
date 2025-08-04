from dataclasses import dataclass
from typing import List, Optional


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
