from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
