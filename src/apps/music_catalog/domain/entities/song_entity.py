from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SongEntity:
    """Entidad que representa una canción"""

    id: str
    title: str
    artist_id: str
    duration_seconds: int
    artist_name: Optional[str] = None
    album_id: Optional[str] = None
    album_title: Optional[str] = None
    file_url: Optional[str] = None  # URL del archivo de audio
    lyrics: Optional[str] = None
    track_number: Optional[int] = None
    genre_id: Optional[str] = None
    genre_name: Optional[str] = None
    play_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
