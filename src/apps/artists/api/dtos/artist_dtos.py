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
<<<<<<< HEAD


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


@dataclass
class SearchArtistsByNameRequestDTO:
    """DTO para búsqueda de artistas por nombre"""

    name: str
    limit: int = 10


@dataclass
class SaveArtistRequestDTO:
    """DTO para guardar un artista desde fuentes externas"""

    name: str
    image_url: Optional[str] = None
    source_type: str = "manual"
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    biography: Optional[str] = None
    country: Optional[str] = None
    channel_id: Optional[str] = None  # Para compatibilidad con YouTube
    channel_url: Optional[str] = None  # Para compatibilidad con YouTube


@dataclass
class SaveArtistResponseDTO:
    """DTO de respuesta para guardar un artista"""

    id: str
    name: str
    image_url: Optional[str] = None
    source_type: str = "manual"
    source_id: Optional[str] = None
    was_created: bool = False  # Indica si fue creado o ya existía


@dataclass
class GetArtistsByCountryRequestDTO:
    """DTO para obtener artistas por país"""

    country: str
    limit: int = 10


@dataclass
class GetPopularArtistsRequestDTO:
    """DTO para obtener artistas populares"""

    limit: int = 10


@dataclass
class GetVerifiedArtistsRequestDTO:
    """DTO para obtener artistas verificados"""

    limit: int = 10
=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
