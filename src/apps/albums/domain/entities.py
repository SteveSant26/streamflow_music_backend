from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class AlbumEntity:
    """Entidad que representa un álbum"""

    id: str
    title: str
    artist_id: str
    artist_name: Optional[str] = None  # Para evitar joins constantes
    release_date: Optional[date] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    total_tracks: int = 0
    play_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
