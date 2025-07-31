from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ArtistResponseDTO:
    """DTO para respuestas de artista"""

    id: str
    name: str
    biography: Optional[str] = None
    country: Optional[str] = None
    image_url: Optional[str] = None
    followers_count: int = 0
    is_verified: bool = False
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class CreateArtistRequestDTO:
    """DTO para crear un artista"""

    name: str
    biography: Optional[str] = None
    country: Optional[str] = None
    image_url: Optional[str] = None


@dataclass
class UpdateArtistRequestDTO:
    """DTO para actualizar un artista"""

    name: Optional[str] = None
    biography: Optional[str] = None
    country: Optional[str] = None
    image_url: Optional[str] = None
    followers_count: Optional[int] = None
    is_verified: Optional[bool] = None
