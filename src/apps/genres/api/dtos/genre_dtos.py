from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class GenreResponseDTO:
    """DTO para respuestas de género"""

    id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    color_hex: Optional[str] = None
    popularity_score: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
