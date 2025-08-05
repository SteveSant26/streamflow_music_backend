from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PlaylistEntity:
    """Entidad de dominio para las playlists"""

    id: str
    name: str
    description: Optional[str]
    user_id: str
    is_default: bool  # Para la playlist "Favoritos" que no se puede eliminar
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones de negocio"""
        if not self.name or not self.name.strip():
            raise ValueError("El nombre de la playlist no puede estar vacío")

        if len(self.name) > 255:
            raise ValueError("El nombre de la playlist no puede exceder 255 caracteres")


@dataclass
class PlaylistSongEntity:
    """Entidad de dominio para las canciones en playlists"""

    id: str
    playlist_id: str
    song_id: str
    position: int
    added_at: datetime

    def __post_init__(self):
        """Validaciones de negocio"""
        if self.position < 0:
            raise ValueError("La posición debe ser un número positivo")
