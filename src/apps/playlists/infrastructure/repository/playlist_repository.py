from typing import List, Optional
from uuid import UUID

from apps.playlists.api.mappers.playlist_entity_model_mapper import (
    PlaylistEntityModelMapper,
)
from apps.playlists.domain.entities import PlaylistEntity, PlaylistSongEntity
from apps.playlists.domain.repository.iplaylist_repository import IPlaylistRepository
from apps.playlists.infrastructure.models import PlaylistModel, PlaylistSongModel
from common.core.repositories import BaseReadOnlyDjangoRepository


class PlaylistRepository(
    BaseReadOnlyDjangoRepository[PlaylistEntity, PlaylistModel], IPlaylistRepository
):
    """Repositorio para gestionar playlists"""

    def __init__(self):
        super().__init__(PlaylistModel, PlaylistEntityModelMapper())

    # Métodos de la interfaz base
    async def save(self, entity: PlaylistEntity) -> PlaylistEntity:
        """Guarda una entidad (create o update según si existe)"""
        if entity.id:
            # Si tiene ID, es una actualización
            return await self.update_playlist(entity)
        else:
            # Si no tiene ID, es una creación
            return await self.create(entity)

    async def update(self, entity_id: str, entity: PlaylistEntity) -> PlaylistEntity:
        """Actualiza una playlist existente usando entity_id como string"""
        entity.id = UUID(entity_id) if isinstance(entity_id, str) else entity_id
        return await self.update_playlist(entity)

    async def delete(self, entity_id: str) -> bool:
        """Elimina una playlist usando entity_id como string"""
        uuid_id = UUID(entity_id) if isinstance(entity_id, str) else entity_id
        return await self.delete_playlist(uuid_id)

    async def create(self, entity: PlaylistEntity) -> PlaylistEntity:
        """Crea una nueva playlist"""
        self.logger.info(f"Creating playlist: {entity.name}")

        model_data = self.mapper.entity_to_model_data(entity)
        model_data.pop("id", None)  # Remover id para que Django genere uno nuevo
        model_data.pop("created_at", None)
        model_data.pop("updated_at", None)

        model = await PlaylistModel.objects.acreate(**model_data)
        return self.mapper.model_to_entity(model)

    async def update_playlist(self, entity: PlaylistEntity) -> PlaylistEntity:
        """Actualiza una playlist existente"""
        self.logger.info(f"Updating playlist: {entity.id}")

        model = await PlaylistModel.objects.aget(id=entity.id)
        model.name = entity.name
        model.description = entity.description
        model.is_public = entity.is_public
        await model.asave()
        return self.mapper.model_to_entity(model)

    async def delete_playlist(self, entity_id: UUID) -> bool:
        """Elimina una playlist (solo si no es default)"""
        self.logger.info(f"Deleting playlist: {entity_id}")
        try:
            model = await PlaylistModel.objects.aget(id=entity_id)
            if model.is_default:
                raise ValueError("No se puede eliminar una playlist por defecto")
            await model.adelete()
            return True
        except PlaylistModel.DoesNotExist:
            return False

    async def get_by_user_id(self, user_id: UUID) -> List[PlaylistEntity]:
        """Obtiene todas las playlists de un usuario"""
        self.logger.debug(f"Getting playlists for user: {user_id}")

        models = [
            model
            async for model in PlaylistModel.objects.filter(user_id=user_id).order_by(
                "created_at"
            )
        ]
        return [self.mapper.model_to_entity(model) for model in models]

    async def get_default_playlist(
        self, user_id: UUID, name: str = "Favoritos"
    ) -> Optional[PlaylistEntity]:
        """Obtiene la playlist por defecto de un usuario (ej: Favoritos)"""
        self.logger.debug(f"Getting default playlist '{name}' for user: {user_id}")

        try:
            model = await PlaylistModel.objects.aget(
                user_id=user_id, name=name, is_default=True
            )
            return self.mapper.model_to_entity(model)
        except PlaylistModel.DoesNotExist:
            return None

    async def create_default_playlist(
        self, user_id: UUID, name: str = "Favoritos"
    ) -> PlaylistEntity:
        """Crea la playlist por defecto para un usuario"""
        self.logger.info(f"Creating default playlist '{name}' for user: {user_id}")

        model = await PlaylistModel.objects.acreate(
            name=name,
            description=f"Tu playlist {name}",
            user_id=user_id,
            is_default=True,
            is_public=False,
        )
        return self.mapper.model_to_entity(model)

    async def add_song_to_playlist(
        self, playlist_id: UUID, song_id: UUID, position: Optional[int] = None
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
            # Mover las canciones siguientes una posición hacia abajo
            async for playlist_song in PlaylistSongModel.objects.filter(
                playlist_id=playlist_id, position__gte=position_to_use
            ):
                playlist_song.position += 1
                await playlist_song.asave()

        model = await PlaylistSongModel.objects.acreate(
            playlist_id=playlist_id, song_id=song_id, position=position_to_use
        )

        return PlaylistSongEntity(
            id=model.id,
            playlist_id=model.playlist.id,
            song_id=model.song.id,
            position=model.position,
            added_at=model.added_at,
        )

    async def remove_song_from_playlist(self, playlist_id: UUID, song_id: UUID) -> bool:
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

    async def get_playlist_songs(self, playlist_id: UUID) -> List[PlaylistSongEntity]:
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
                id=model.id,
                playlist_id=model.playlist.id,
                song_id=model.song.id,
                position=model.position,
                added_at=model.added_at,
            )
            for model in models
        ]

    # Métodos adicionales requeridos por la interfaz
    async def reorder_playlist_songs(
        self, playlist_id: UUID, song_positions: List[tuple[UUID, int]]
    ) -> bool:
        """Reordena las canciones de una playlist"""
        self.logger.info(f"Reordering songs in playlist: {playlist_id}")

        try:
            for song_id, new_position in song_positions:
                playlist_song = await PlaylistSongModel.objects.aget(
                    playlist_id=playlist_id, song_id=song_id
                )
                playlist_song.position = new_position
                await playlist_song.asave()
            return True
        except Exception as e:
            self.logger.error(f"Error reordering songs: {e}")
            return False

    async def get_public_playlists(
        self, limit: int = 20, offset: int = 0
    ) -> List[PlaylistEntity]:
        """Obtiene playlists públicas"""
        self.logger.debug(
            f"Getting public playlists with limit: {limit}, offset: {offset}"
        )

        models = [
            model
            async for model in PlaylistModel.objects.filter(is_public=True).order_by(
                "-created_at"
            )[offset : offset + limit]
        ]
        return [self.mapper.model_to_entity(model) for model in models]

    async def search_playlists(
        self, query: str, user_id: Optional[UUID] = None, limit: int = 20
    ) -> List[PlaylistEntity]:
        """Busca playlists por nombre o descripción"""
        self.logger.debug(f"Searching playlists with query: {query}")

        from django.db.models import Q

        queryset = PlaylistModel.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

        if user_id:
            queryset = queryset.filter(Q(user_id=user_id) | Q(is_public=True))
        else:
            queryset = queryset.filter(is_public=True)

        models = [model async for model in queryset.order_by("-created_at")[:limit]]
        return [self.mapper.model_to_entity(model) for model in models]

    async def get_playlist_song_count(self, playlist_id: UUID) -> int:
        """Obtiene el número de canciones en una playlist"""
        self.logger.debug(f"Getting song count for playlist: {playlist_id}")

        return await PlaylistSongModel.objects.filter(playlist_id=playlist_id).acount()

    async def is_song_in_playlist(self, playlist_id: UUID, song_id: UUID) -> bool:
        """Verifica si una canción está en una playlist específica"""
        self.logger.debug(f"Checking if song {song_id} is in playlist {playlist_id}")

        return await PlaylistSongModel.objects.filter(
            playlist_id=playlist_id, song_id=song_id
        ).aexists()
