from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ArtistEntity:
    """Entidad que representa un artista"""

    id: str
    name: str
    biography: Optional[str] = None
    country: Optional[str] = None
    image_url: Optional[str] = None
    followers_count: int = 0
    is_verified: bool = False
    is_active: bool = True

    # Metadatos de origen (para identificar la fuente externa)
    source_type: str = "manual"  # manual, youtube, spotify, etc.
    source_id: Optional[str] = None  # ID del canal de YouTube u otra fuente
    source_url: Optional[str] = None  # URL del perfil en la fuente original

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
