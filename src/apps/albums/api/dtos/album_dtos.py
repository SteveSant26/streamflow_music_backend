from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class AlbumResponseDTO:
    """DTO para respuestas de álbum"""

    id: str
    title: str
    artist_id: str
    artist_name: Optional[str] = None
    release_date: Optional[date] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    total_tracks: int = 0
    play_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class AlbumSearchRequestDTO:
    """DTO para búsqueda de álbumes"""

    q: str
    artist_id: Optional[str] = None
    artist_name: Optional[str] = None
    limit: int = 10


@dataclass
class AlbumSearchResponseDTO:
    """DTO para respuesta de búsqueda de álbumes"""

    source: str  # "local_cache", "youtube_api", "not_found"
    results: list
    message: Optional[str] = None
