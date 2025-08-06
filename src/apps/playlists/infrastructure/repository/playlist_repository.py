from typing import List, Optional

from asgiref.sync import sync_to_async
from django.db import models

from apps.playlists.api.mappers.playlist_entity_model_mapper import (
    PlaylistEntityModelMapper,
)
from apps.playlists.domain.entities import PlaylistEntity, PlaylistSongEntity
from apps.playlists.domain.repository.iplaylist_repository import IPlaylistRepository
from apps.playlists.infrastructure.models import PlaylistModel, PlaylistSongModel
from common.core.repositories import BaseDjangoRepository


class PlaylistRepository(
    BaseDjangoRepository[PlaylistEntity, PlaylistModel], IPlaylistRepository
):
    """Repositorio para gestionar playlists"""

    def __init__(self):
        super().__init__(PlaylistModel, PlaylistEntityModelMapper())

    async def create(self, entity: PlaylistEntity) -> PlaylistEntity:
        """Crea una nueva playlist"""
        self.logger.info(f"Creating playlist: {entity.name}")

        model_data = self.mapper.entity_to_model_data(entity)
        model_data.pop("created_at", None)
        model_data.pop("updated_at", None)

        model = await PlaylistModel.objects.acreate(**model_data)
        return await sync_to_async(self.mapper.model_to_entity)(model)

    async def update_playlist(self, entity: PlaylistEntity) -> PlaylistEntity:
        """Actualiza una playlist existente usando la entidad completa"""
        self.logger.info(f"Updating playlist: {entity.id}")

        model = await PlaylistModel.objects.select_related("user").aget(id=entity.id)
        model.name = entity.name
        model.description = entity.description
        model.is_public = entity.is_public
        await model.asave()
        return self.mapper.model_to_entity(model)

    async def delete_playlist(self, entity_id: str) -> bool:
        """Elimina una playlist usando string ID (solo si no es default)"""
        self.logger.info(f"Deleting playlist: {entity_id}")
        try:
            model = await PlaylistModel.objects.select_related("user").aget(
                id=entity_id
            )
            if model.is_default:
                raise ValueError("No se puede eliminar una playlist por defecto")
            await model.adelete()
            return True
        except PlaylistModel.DoesNotExist:
            return False

    async def get_by_user_id(self, user_id: str) -> List[PlaylistEntity]:
        """Obtiene todas las playlists de un usuario"""
        self.logger.debug(f"Getting playlists for user: {user_id}")

        models = []
        async for model in (
            PlaylistModel.objects.filter(user__id=user_id)
            .select_related("user")
            .order_by("created_at")
        ):
            models.append(model)

        return [self.mapper.model_to_entity(model) for model in models]

    async def get_default_playlist(
        self, user_id: str, name: str = "Favoritos"
    ) -> Optional[PlaylistEntity]:
        """Obtiene la playlist por defecto de un usuario (ej: Favoritos)"""
        self.logger.debug(f"Getting default playlist '{name}' for user: {user_id}")

        try:
            model = await PlaylistModel.objects.select_related("user").aget(
                user__id=user_id, name=name, is_default=True
            )
            return self.mapper.model_to_entity(model)
        except PlaylistModel.DoesNotExist:
            return None

    async def create_default_playlist(
        self, user_id: str, name: str = "Favoritos"
    ) -> PlaylistEntity:
        """Crea la playlist por defecto para un usuario"""
        self.logger.info(f"Creating default playlist '{name}' for user: {user_id}")

        # Obtener la instancia del usuario
        from apps.user_profile.infrastructure.models.user_profile import (
            UserProfileModel,
        )

        user_instance = await UserProfileModel.objects.aget(id=user_id)

        model = await PlaylistModel.objects.acreate(
            name=name,
            description=f"Tu playlist {name}",
            user=user_instance,
            is_default=True,
            is_public=False,
        )
        return self.mapper.model_to_entity(model)

    async def add_song_to_playlist(
        self, playlist_id: str, song_id: str, position: Optional[int] = None
    ) -> PlaylistSongEntity:
        """Añade una canción a una playlist"""
        self.logger.info(f"Adding song {song_id} to playlist {playlist_id}")

        # Verificar si la canción ya está en la playlist
        existing = await PlaylistSongModel.objects.filter(
            playlist_id=playlist_id, song_id=song_id
        ).afirst()

        if existing:
            raise ValueError("La canción ya está en esta playlist")

        # Si no se especifica posición, agregar al final
        if position is None:
            position_to_use = (
                await PlaylistSongModel.objects.filter(playlist_id=playlist_id).acount()
                + 1
            )
        else:
            position_to_use = position
            # Para evitar violación de constraint único, utilizamos una estrategia diferente:
            # 1. Primero encontramos el máximo de posiciones actual
            # 2. Movemos todos los elementos a posiciones temporales altas
            # 3. Luego los reordenamos correctamente

            # Obtener el máximo de posiciones actual
            max_position = await sync_to_async(
                PlaylistSongModel.objects.filter(playlist_id=playlist_id).aggregate
            )(max_pos=models.Max("position"))
            max_pos = max_position["max_pos"] or 0

            # Obtener todas las canciones que necesitan moverse
            songs_to_move = [
                song
                async for song in PlaylistSongModel.objects.filter(
                    playlist_id=playlist_id, position__gte=position_to_use
                ).order_by("position")
            ]

            # Mover a posiciones temporales altas para evitar conflictos
            temp_position = max_pos + 1000  # Usar posiciones muy altas temporalmente
            for song in songs_to_move:
                song.position = temp_position
                await song.asave()
                temp_position += 1

            # Ahora mover a las posiciones finales correctas
            final_position = position_to_use + 1
            for song in songs_to_move:
                song.position = final_position
                await song.asave()
                final_position += 1

        model = await PlaylistSongModel.objects.acreate(
            playlist_id=playlist_id, song_id=song_id, position=position_to_use
        )

        return PlaylistSongEntity(
            id=str(model.id),
            playlist_id=playlist_id,
            song_id=song_id,
            position=model.position,
            added_at=model.added_at,
        )

    async def remove_song_from_playlist(self, playlist_id: str, song_id: str) -> bool:
        """Remueve una canción de una playlist"""
        self.logger.info(f"Removing song {song_id} from playlist {playlist_id}")

        try:
            playlist_song = await PlaylistSongModel.objects.aget(
                playlist_id=playlist_id, song_id=song_id
            )
            position = playlist_song.position
            await playlist_song.adelete()

            # Mover las canciones siguientes una posición hacia arriba
            async for song in PlaylistSongModel.objects.filter(
                playlist_id=playlist_id, position__gt=position
            ):
                song.position -= 1
                await song.asave()

            return True
        except PlaylistSongModel.DoesNotExist:
            return False

    async def get_playlist_songs(self, playlist_id: str) -> List[PlaylistSongEntity]:
        """Obtiene todas las canciones de una playlist"""
        self.logger.debug(f"Getting songs for playlist: {playlist_id}")

        models = [
            model
            async for model in PlaylistSongModel.objects.filter(
                playlist_id=playlist_id
            ).order_by("position")
        ]
        return [
            PlaylistSongEntity(
                id=str(model.id),
                playlist_id=playlist_id,
                song_id=str(
                    model.song_id  # pyright: ignore[reportAttributeAccessIssue]
                ),
                position=model.position,
                added_at=model.added_at,
            )
            for model in models
        ]

    async def get_public_playlists(
        self,
    ) -> List[PlaylistEntity]:
        """Obtiene playlists públicas"""
        self.logger.debug("Getting public playlists")

        models = []
        async for model in (
            PlaylistModel.objects.filter(is_public=True)
            .select_related("user")
            .order_by("-created_at")
        ):
            models.append(model)
        return [self.mapper.model_to_entity(model) for model in models]

    async def search_playlists(
        self, query: str, user_id: Optional[str] = None, limit: int = 20
    ) -> List[PlaylistEntity]:
        """Busca playlists por nombre o descripción"""
        self.logger.debug(f"Searching playlists with query: {query}")

        from django.db.models import Q

        queryset = PlaylistModel.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

        if user_id:
            queryset = queryset.filter(Q(user__id=user_id) | Q(is_public=True))
        else:
            queryset = queryset.filter(is_public=True)

        models = []
        async for model in queryset.select_related("user").order_by("-created_at")[
            :limit
        ]:
            models.append(model)
        return [self.mapper.model_to_entity(model) for model in models]

    async def is_song_in_playlist(self, playlist_id: str, song_id: str) -> bool:
        """Verifica si una canción está en una playlist específica"""
        self.logger.debug(f"Checking if song {song_id} is in playlist {playlist_id}")

        return await PlaylistSongModel.objects.filter(
            playlist_id=playlist_id, song_id=song_id
        ).aexists()
