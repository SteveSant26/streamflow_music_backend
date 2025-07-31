from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class GenreEntity:
    """Entidad que representa un género musical"""

    id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    song_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
