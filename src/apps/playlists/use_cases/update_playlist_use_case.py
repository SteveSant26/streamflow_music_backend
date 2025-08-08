from typing import Any, Dict

from common.interfaces.ibase_use_case import BaseUseCase
from common.interfaces.istorage_service import IStorageService
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import UpdatePlaylistRequestDTO
from ..domain.entities import PlaylistEntity
from ..domain.exceptions import PlaylistValidationException
from ..domain.repository.iplaylist_repository import IPlaylistRepository


class UpdatePlaylistUseCase(BaseUseCase[Dict[str, Any], PlaylistEntity]):
    """Caso de uso para actualizar una playlist"""

    def __init__(
        self, playlist_repository: IPlaylistRepository, storage_service: IStorageService
    ):
        super().__init__()
        self.repository = playlist_repository
        self.storage_service = storage_service

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(
        self, user_id, update_dto: UpdatePlaylistRequestDTO
    ) -> PlaylistEntity:
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
            playlist_id = update_dto.playlist_id

            if not playlist_id or not user_id or not update_dto:
                raise PlaylistValidationException(
                    "playlist_id, user_id y update_dto son requeridos"
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

            playlist_img_path = existing_playlist.playlist_img
            if update_dto.playlist_img_file:
                file_path = f"playlist_{playlist_id}.jpg"
                upload_success = self.storage_service.upload_item(
                    file_path, update_dto.playlist_img_file
                )
                if not upload_success:
                    raise PlaylistValidationException(
                        "Error al subir la imagen de la playlist"
                    )

                playlist_img_path = file_path

            is_public_value = update_dto.is_public
            if isinstance(is_public_value, str):
                is_public_value = is_public_value.lower() == "true"

            # Crear entidad actualizada
            updated_playlist = PlaylistEntity(
                id=existing_playlist.id,
                name=update_dto.name or existing_playlist.name,
                description=(
                    update_dto.description
                    if update_dto.description is not None
                    else existing_playlist.description
                ),
                user_id=existing_playlist.user_id,
                is_default=existing_playlist.is_default,
                is_public=is_public_value,  # type: ignore
                playlist_img=playlist_img_path,
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
