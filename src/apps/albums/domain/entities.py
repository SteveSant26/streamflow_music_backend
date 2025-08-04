from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class AlbumEntity:
    """Entidad que representa un álbum"""

    id: str
    title: str
    artist_id: Optional[str] = None
    artist_name: Optional[str] = None  # Para evitar joins constantes
    release_date: Optional[date] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    total_tracks: int = 0
    play_count: int = 0

    # Metadatos de origen (para identificar la fuente externa)
    source_type: str = "manual"  # manual, youtube, spotify, etc.
    source_id: Optional[str] = None  # ID del álbum en la fuente externa
    source_url: Optional[str] = None  # URL del álbum en la fuente original

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
