from typing import Any, Dict

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import UpdatePlaylistRequestDTO
from ..domain.entities import PlaylistEntity
from ..domain.exceptions import PlaylistValidationException
from ..domain.repository.iplaylist_repository import IPlaylistRepository


class UpdatePlaylistUseCase(BaseUseCase[Dict[str, Any], PlaylistEntity]):
    """Caso de uso para actualizar una playlist"""

    def __init__(self, playlist_repository: IPlaylistRepository):
        super().__init__()
        self.repository = playlist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(self, request_data: Dict[str, Any]) -> PlaylistEntity:
        """
        Actualiza una playlist existente

        Args:
            request_data: Diccionario con playlist_id, user_id y update_dto

        Returns:
            PlaylistEntity actualizada

        Raises:
            PlaylistValidationException: Si los datos son inválidos
        """
        try:
            playlist_id = request_data.get("playlist_id")
            user_id = request_data.get("user_id")
            update_dto = request_data.get("update_dto")

            if not playlist_id or not user_id or not update_dto:
                raise PlaylistValidationException(
                    "playlist_id, user_id y update_dto son requeridos"
                )

            if not isinstance(update_dto, UpdatePlaylistRequestDTO):
                raise PlaylistValidationException(
                    "update_dto debe ser del tipo UpdatePlaylistRequestDTO"
                )

            # Verificar que la playlist existe y pertenece al usuario
            existing_playlist = await self.repository.get_by_id(playlist_id)
            if not existing_playlist:
                raise PlaylistValidationException("Playlist no encontrada")

            if existing_playlist.user_id != user_id:
                raise PlaylistValidationException(
                    "No tienes permisos para modificar esta playlist"
                )

            # No permitir modificar el nombre de playlists por defecto
            if (
                existing_playlist.is_default
                and update_dto.name != existing_playlist.name
            ):
                raise PlaylistValidationException(
                    "No se puede cambiar el nombre de la playlist de favoritos"
                )

            # Crear entidad actualizada
            updated_playlist = PlaylistEntity(
                id=existing_playlist.id,
                name=update_dto.name or existing_playlist.name,
                description=update_dto.description
                if update_dto.description is not None
                else existing_playlist.description,
                user_id=existing_playlist.user_id,
                is_default=existing_playlist.is_default,
                is_public=update_dto.is_public
                if update_dto.is_public is not None
                else existing_playlist.is_public,
                created_at=existing_playlist.created_at,
                updated_at=existing_playlist.updated_at,
            )

            # Actualizar en el repositorio
            return await self.repository.update_playlist(updated_playlist)

        except PlaylistValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Error actualizando playlist: {str(e)}")
            raise PlaylistValidationException(f"Error interno: {str(e)}")
