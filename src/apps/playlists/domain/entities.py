from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class PlaylistEntity:
    """Entidad de dominio para las playlists"""

    id: str  # ID generado por la base de datos
    name: str
    description: Optional[str]
    user_id: str
    is_default: bool  # Para la playlist "Favoritos" que no se puede eliminar
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    songs: Optional[List["PlaylistSongEntity"]] = None  # Relación con canciones

    def __post_init__(self):
        """Validaciones de negocio"""
        if not self.name or not self.name.strip():
            raise ValueError("El nombre de la playlist no puede estar vacío")

        if len(self.name) > 255:
            raise ValueError("El nombre de la playlist no puede exceder 255 caracteres")

    @property
    def song_count(self) -> int:
        """Retorna el número de canciones en la playlist"""
        return len(self.songs) if self.songs else 0

    def add_song(self, song_entity: "PlaylistSongEntity") -> None:
        """Añade una canción a la playlist"""
        if self.songs is None:
            self.songs = []
        self.songs.append(song_entity)

    def remove_song(self, song_id: str) -> None:
        """Remueve una canción de la playlist"""
        if self.songs:
            self.songs = [song for song in self.songs if song.song_id != song_id]

    def get_song_by_id(self, song_id: str) -> Optional["PlaylistSongEntity"]:
        """Obtiene una canción específica de la playlist"""
        if self.songs:
            return next((song for song in self.songs if song.song_id == song_id), None)
        return None

    def reorder_songs(self, new_positions: List[tuple[str, int]]) -> None:
        """Reordena las canciones según las nuevas posiciones"""
        if not self.songs:
            return

        # Crear un diccionario para mapear song_id -> nueva_posición
        position_map = dict(new_positions)

        # Actualizar las posiciones de las canciones
        for song in self.songs:
            if song.song_id in position_map:
                song.position = position_map[song.song_id]

        # Ordenar por posición
        self.songs.sort(key=lambda x: x.position)


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
