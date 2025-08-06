from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class AlbumResponseDTO:
    """DTO para respuestas de álbum"""

    id: str
    title: str
    artist_id: Optional[str] = None
    artist_name: Optional[str] = None
    release_date: Optional[date] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    total_tracks: int = 0
    play_count: int = 0

    # Metadatos de origen
    source_type: str = "manual"
    source_id: Optional[str] = None
    source_url: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
