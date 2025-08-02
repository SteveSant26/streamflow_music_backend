from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ExtractedArtistInfo:
    """Información de artista extraída de metadatos de video"""

    name: str
    channel_id: Optional[str] = None
    extracted_from: str = "title"  # "title", "description", "channel"
    confidence_score: float = 0.0  # 0.0 a 1.0
    additional_info: Optional[Dict[str, Any]] = None


@dataclass
class ExtractedAlbumInfo:
    """Información de álbum extraída de metadatos de video"""

    title: str
    artist_name: Optional[str] = None
    extracted_from: str = "title"  # "title", "description", "tags"
    confidence_score: float = 0.0  # 0.0 a 1.0
    release_year: Optional[int] = None
    additional_info: Optional[Dict[str, Any]] = None
