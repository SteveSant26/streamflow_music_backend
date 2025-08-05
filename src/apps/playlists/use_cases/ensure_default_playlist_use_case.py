from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import PlaylistEntity
from ..domain.exceptions import PlaylistValidationException
from ..domain.repository.iplaylist_repository import IPlaylistRepository


class EnsureDefaultPlaylistUseCase(BaseUseCase[str, PlaylistEntity]):
    """Caso de uso para asegurar que un usuario tenga una playlist por defecto"""

    def __init__(self, playlist_repository: IPlaylistRepository):
        super().__init__()
        self.repository = playlist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(self, user_id: str) -> PlaylistEntity:
        """
        Asegura que un usuario tenga una playlist por defecto (Favoritos)

        Args:
            user_id: ID del usuario

        Returns:
            Entidad de playlist por defecto (existente o recién creada)

        Raises:
            PlaylistValidationException: Si el user_id es inválido
        """
        try:
            if not user_id:
                raise PlaylistValidationException("El ID del usuario es requerido")

            # Verificar si ya existe una playlist por defecto
            existing = await self.repository.get_default_playlist(user_id, "Favoritos")
            if existing:
                self.logger.info(
                    f"Default playlist 'Favoritos' already exists for user {user_id}"
                )
                return existing

            # Si no existe, crear una nueva
            self.logger.info(
                f"Creating default playlist 'Favoritos' for user {user_id}"
            )
            return await self.repository.create_default_playlist(user_id, "Favoritos")

        except Exception as e:
            self.logger.error(f"Error ensuring default playlist: {str(e)}")
            raise
