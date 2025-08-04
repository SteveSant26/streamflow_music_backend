from uuid import UUID

from apps.playlists.infrastructure.repository import PlaylistRepository
from common.interfaces.ibase_use_case import BaseUseCase


class EnsureDefaultPlaylistUseCase(BaseUseCase[UUID, None]):
    """Caso de uso para asegurar que un usuario tenga su playlist de favoritos"""
    
    def __init__(self, playlist_repository: PlaylistRepository):
        super().__init__()
        self.playlist_repository = playlist_repository
    
    async def execute(self, user_id: UUID) -> None:
        """Asegura que el usuario tenga una playlist de favoritos"""
        self.logger.info(f"Ensuring default playlist for user {user_id}")
        
        # Verificar si ya existe la playlist de favoritos
        favorites_playlist = await self.playlist_repository.get_default_playlist(
            user_id, "Favoritos"
        )
        
        if not favorites_playlist:
            # Crear la playlist de favoritos
            await self.playlist_repository.create_default_playlist(user_id, "Favoritos")
            self.logger.info(f"Created default 'Favoritos' playlist for user {user_id}")
        else:
            self.logger.debug(f"Default playlist already exists for user {user_id}")
