from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class SongEntity:
    """Entidad que representa una canción en la aplicación"""

    id: str
    title: str
    album_id: Optional[str] = None
    artist_id: Optional[str] = None
    genre_ids: Optional[List[str]] = None  # Lista de IDs de géneros
    duration_seconds: int = 0
    album_title: Optional[str] = None  # Desnormalizado para consultas rápidas
    artist_name: Optional[str] = None  # Desnormalizado para consultas rápidas
    genre_names: Optional[
        List[str]
    ] = None  # Lista de nombres de géneros (desnormalizado)
    track_number: Optional[int] = None
    file_url: Optional[str] = None  # URL del archivo de audio en Supabase
    thumbnail_url: Optional[str] = None  # URL de la imagen en Supabase
    lyrics: Optional[str] = None

    # Métricas internas de la aplicación
    play_count: int = 0  # Reproducciones en nuestra app
    favorite_count: int = 0  # Veces agregada a favoritos
    download_count: int = 0  # Veces descargada

    # Metadatos de origen (solo para referencia)
    source_type: str = "youtube"  # youtube, upload, etc.
    source_id: Optional[str] = None  # ID del video de YouTube u otra fuente
    source_url: Optional[str] = None  # URL original

    # Estados y configuración
    is_explicit: bool = False
    is_active: bool = True
    is_premium: bool = False  # Si requiere suscripción premium
    audio_quality: str = "standard"  # standard, high, lossless

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_played_at: Optional[datetime] = None
    release_date: Optional[datetime] = None

    def __post_init__(self):
        if self.genre_ids is None:
            self.genre_ids = []
        if self.genre_names is None:
            self.genre_names = []
