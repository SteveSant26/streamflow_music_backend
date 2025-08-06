from abc import abstractmethod
from typing import Any, List, Optional

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import PlaylistEntity, PlaylistSongEntity


class IPlaylistRepository(IBaseRepository[PlaylistEntity, Any]):
    """Interface para el repositorio de playlists"""

    # Métodos específicos del dominio de playlists
    @abstractmethod
    async def create(self, entity: PlaylistEntity) -> PlaylistEntity:
        """Crea una nueva playlist"""

    @abstractmethod
    async def update_playlist(self, entity: PlaylistEntity) -> PlaylistEntity:
        """Actualiza una playlist existente usando la entidad completa"""

    @abstractmethod
    async def delete_playlist(self, entity_id: str) -> bool:
        """Elimina una playlist usando string ID (solo si no es default)"""

    # Métodos específicos del dominio de playlists
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[PlaylistEntity]:
        """Obtiene todas las playlists de un usuario"""

    @abstractmethod
    async def get_default_playlist(
        self, user_id: str, name: str = "Favoritos"
    ) -> Optional[PlaylistEntity]:
        """Obtiene la playlist por defecto de un usuario (ej: Favoritos)"""

    @abstractmethod
    async def create_default_playlist(
        self, user_id: str, name: str = "Favoritos"
    ) -> PlaylistEntity:
        """Crea la playlist por defecto para un usuario"""

    # Métodos para gestionar canciones en playlists
    @abstractmethod
    async def add_song_to_playlist(
        self, playlist_id: str, song_id: str, position: Optional[int] = None
    ) -> PlaylistSongEntity:
        """Añade una canción a una playlist"""

    @abstractmethod
    async def remove_song_from_playlist(self, playlist_id: str, song_id: str) -> bool:
        """Remueve una canción de una playlist"""

    @abstractmethod
    async def get_playlist_songs(self, playlist_id: str) -> List[PlaylistSongEntity]:
        """Obtiene todas las canciones de una playlist"""

    @abstractmethod
    async def get_public_playlists(
        self,
    ) -> List[PlaylistEntity]:
        """Obtiene playlists públicas"""

    @abstractmethod
    async def search_playlists(
        self, query: str, user_id: Optional[str] = None, limit: int = 20
    ) -> List[PlaylistEntity]:
        """Busca playlists por nombre o descripción"""

    @abstractmethod
    async def get_playlist_song_count(self, playlist_id: str) -> int:
        """Obtiene el número de canciones en una playlist"""

    @abstractmethod
    async def is_song_in_playlist(self, playlist_id: str, song_id: str) -> bool:
        """Verifica si una canción está en una playlist específica"""
