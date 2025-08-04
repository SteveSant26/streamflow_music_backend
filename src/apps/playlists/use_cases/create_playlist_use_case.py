import uuid
from typing import List
from uuid import UUID

from apps.playlists.api.dtos.playlist_dtos import PlaylistCreateRequestDTO
from apps.playlists.domain.entities import PlaylistEntity
from apps.playlists.infrastructure.repository import PlaylistRepository
from common.interfaces.ibase_use_case import BaseUseCase


class CreatePlaylistUseCase(BaseUseCase[PlaylistCreateRequestDTO, PlaylistEntity]):
    """Caso de uso para crear una nueva playlist"""
    
    def __init__(self, playlist_repository: PlaylistRepository):
        super().__init__()
        self.playlist_repository = playlist_repository
    
    async def execute(self, request: PlaylistCreateRequestDTO, user_id: UUID) -> PlaylistEntity:
        """Crea una nueva playlist para el usuario"""
        self.logger.info(f"Creating playlist '{request.name}' for user {user_id}")
        
        # Crear la entidad de playlist
        playlist_entity = PlaylistEntity(
            id=uuid.uuid4(),
            name=request.name,
            description=request.description,
            user_id=user_id,
            is_default=False,  # Las playlists creadas por el usuario nunca son default
            is_public=request.is_public,
            created_at=None,  # Se asignará en el modelo
            updated_at=None,
        )
        
        # Guardar en el repositorio
        created_playlist = await self.playlist_repository.create(playlist_entity)
        
        self.logger.info(f"Successfully created playlist {created_playlist.id}")
        return created_playlist
