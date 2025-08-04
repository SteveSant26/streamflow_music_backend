from uuid import UUID

from apps.playlists.api.dtos.playlist_dtos import PlaylistUpdateRequestDTO
from apps.playlists.domain.entities import PlaylistEntity
from apps.playlists.infrastructure.repository import PlaylistRepository
from common.interfaces.ibase_use_case import BaseUseCase


class UpdatePlaylistUseCase(BaseUseCase[dict, PlaylistEntity]):
    """Caso de uso para actualizar una playlist"""
    
    def __init__(self, playlist_repository: PlaylistRepository):
        super().__init__()
        self.playlist_repository = playlist_repository
    
    async def execute(self, request: dict) -> PlaylistEntity:
        """
        Actualiza una playlist
        
        Args:
            request: dict con 'playlist_id' y 'update_data' (PlaylistUpdateRequestDTO)
        """
        playlist_id = request["playlist_id"]
        update_data: PlaylistUpdateRequestDTO = request["update_data"]
        
        self.logger.info(f"Updating playlist {playlist_id}")
        
        # Obtener la playlist actual
        current_playlist = await self.playlist_repository.get_by_id(playlist_id)
        if not current_playlist:
            raise ValueError(f"Playlist {playlist_id} no encontrada")
        
        # No permitir actualizar playlists default
        if current_playlist.is_default:
            raise ValueError("No se puede modificar una playlist por defecto")
        
        # Aplicar los cambios
        updated_playlist = PlaylistEntity(
            id=current_playlist.id,
            name=update_data.name if update_data.name is not None else current_playlist.name,
            description=update_data.description if update_data.description is not None else current_playlist.description,
            user_id=current_playlist.user_id,
            is_default=current_playlist.is_default,
            is_public=update_data.is_public if update_data.is_public is not None else current_playlist.is_public,
            created_at=current_playlist.created_at,
            updated_at=current_playlist.updated_at,
        )
        
        # Guardar los cambios
        result = await self.playlist_repository.update(updated_playlist)
        
        self.logger.info(f"Successfully updated playlist {playlist_id}")
        return result
