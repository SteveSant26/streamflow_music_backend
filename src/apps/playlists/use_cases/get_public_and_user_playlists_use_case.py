from typing import List

from django.db.models import Q, QuerySet

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
    async def execute(self, queryset: QuerySet, user_id: str) -> List[PlaylistEntity]:
        """
        Ejecuta el caso de uso para obtener playlists públicas y del usuario,
        aplicando los filtros del queryset.

        Args:
            queryset: El QuerySet de Django, pre-filtrado por la vista.
            user_id: ID del usuario autenticado (opcional).

        Returns:
            Lista de entidades de playlist (públicas + del usuario).
        """
        self.logger.info(f"Getting playlists for user: {user_id}")

        try:
            if user_id:
                # Usa un Q object para combinar filtros en el queryset de manera eficiente.
                # Busca playlists públicas o playlists del usuario autenticado.
                combined_filter = Q(is_public=True) | Q(user__id=user_id)
                final_queryset = queryset.filter(combined_filter)

                # El repositorio se encarga de ejecutar el queryset y mapear a entidades.
                playlists = await self.playlist_repository.get_from_queryset(
                    final_queryset
                )

                self.logger.info(
                    f"Retrieved {len(playlists)} combined playlists for user: {user_id}"
                )
                return playlists
            else:
                # Para usuarios anónimos, solo se buscan las playlists públicas.
                public_playlists_queryset = queryset.filter(is_public=True)
                playlists = await self.playlist_repository.get_from_queryset(
                    public_playlists_queryset
                )

                self.logger.info(f"Retrieved {len(playlists)} public playlists")
                return playlists

        except Exception as e:
            self.logger.error(f"Error getting public and user playlists: {str(e)}")
            raise e
