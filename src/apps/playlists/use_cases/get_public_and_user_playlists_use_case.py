from typing import List

from apps.playlists.domain.entities import PlaylistEntity
from apps.playlists.domain.repository.iplaylist_repository import IPlaylistRepository
from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance


class GetPublicAndUserPlaylistsUseCase(BaseUseCase[dict, List[PlaylistEntity]]):
    """
    Caso de uso para obtener playlists públicas y del usuario autenticado.
    Retorna todas las playlists públicas junto con las playlists del usuario
    (tanto públicas como privadas), eliminando duplicados.
    """

    def __init__(self, playlist_repository: IPlaylistRepository):
        super().__init__()
        self.playlist_repository = playlist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(self, params: dict) -> List[PlaylistEntity]:
        """
        Ejecuta el caso de uso para obtener playlists públicas y del usuario.

        Args:
            params: Diccionario con parámetros:
                - user_id: ID del usuario autenticado (opcional)
                - limit: Límite de playlists públicas a obtener (default: 50)
                - offset: Offset para paginación de playlists públicas (default: 0)

        Returns:
            Lista de entidades de playlist (públicas + del usuario)
        """
        user_id = params.get("user_id")

        self.logger.info(f"Getting public and user playlists for user: {user_id}")

        try:
            # Obtener playlists públicas
            public_playlists = await self.playlist_repository.get_public_playlists()

            # Si hay usuario autenticado, obtener también sus playlists
            if user_id:
                user_playlists = await self.playlist_repository.get_by_user_id(user_id)

                # Crear un conjunto para evitar duplicados (playlists públicas del usuario)
                playlist_ids = set()
                combined_playlists = []

                # Primero agregar las playlists del usuario (tienen prioridad)
                for playlist in user_playlists:
                    combined_playlists.append(playlist)
                    playlist_ids.add(playlist.id)

                # Luego agregar las playlists públicas que no sean del usuario
                for playlist in public_playlists:
                    if playlist.id not in playlist_ids:
                        combined_playlists.append(playlist)

                # Ordenar por fecha de creación (más recientes primero)
                combined_playlists.sort(key=lambda p: p.created_at, reverse=True)

                self.logger.info(
                    f"Retrieved {len(combined_playlists)} playlists "
                    f"({len(user_playlists)} user, {len(public_playlists)} public)"
                )

                return combined_playlists
            else:
                # Si no hay usuario autenticado, solo devolver playlists públicas
                self.logger.info(f"Retrieved {len(public_playlists)} public playlists")
                return public_playlists

        except Exception as e:
            self.logger.error(f"Error getting public and user playlists: {str(e)}")
            raise e
