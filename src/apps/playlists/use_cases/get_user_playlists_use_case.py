from typing import List
from uuid import UUID

from apps.playlists.domain.entities import PlaylistEntity
from apps.playlists.infrastructure.repository import PlaylistRepository
from common.interfaces.ibase_use_case import BaseUseCase


class GetUserPlaylistsUseCase(BaseUseCase[UUID, List[PlaylistEntity]]):
    """Caso de uso para obtener las playlists de un usuario"""
    
    def __init__(self, playlist_repository: PlaylistRepository):
        super().__init__()
        self.playlist_repository = playlist_repository
    
    async def execute(self, user_id: UUID) -> List[PlaylistEntity]:
        """Obtiene todas las playlists del usuario"""
        self.logger.info(f"Getting playlists for user {user_id}")
        
        playlists = await self.playlist_repository.get_by_user_id(user_id)
        
        self.logger.info(f"Found {len(playlists)} playlists for user {user_id}")
        return playlists
