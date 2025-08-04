from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ArtistResponseDTO:
    """DTO para respuestas de artista"""

    id: str
    name: str
    biography: Optional[str] = None
    image_url: Optional[str] = None
    followers_count: int = 0
    is_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
