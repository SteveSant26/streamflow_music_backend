from typing import List, Optional
from uuid import UUID

from asgiref.sync import sync_to_async
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.playlists.api.mappers.playlist_entity_model_mapper import PlaylistEntityModelMapper
from apps.playlists.domain.entities import PlaylistEntity, PlaylistSongEntity
from apps.playlists.infrastructure.models import PlaylistModel, PlaylistSongModel
from common.core.repositories import BaseReadOnlyDjangoRepository
from common.interfaces.ibase_repository import IWriteOnlyRepository


class PlaylistRepository(
    BaseReadOnlyDjangoRepository[PlaylistEntity, PlaylistModel],
    IWriteOnlyRepository[PlaylistEntity]
):
    """Repositorio para gestionar playlists"""
    
    def __init__(self):
        mapper = PlaylistEntityModelMapper()
        super().__init__(PlaylistModel, mapper)
    
    async def create(self, entity: PlaylistEntity) -> PlaylistEntity:
        """Crea una nueva playlist"""
        self.logger.info(f"Creating playlist: {entity.name}")
        
        model_data = self.mapper.entity_to_model_data(entity)
        model_data.pop('id', None)  # Remover id para que Django genere uno nuevo
        model_data.pop('created_at', None)
        model_data.pop('updated_at', None)
        
        model = await sync_to_async(PlaylistModel.objects.create)(**model_data)
        return self.mapper.model_to_entity(model)
    
    async def update(self, entity: PlaylistEntity) -> PlaylistEntity:
        """Actualiza una playlist existente"""
        self.logger.info(f"Updating playlist: {entity.id}")
        
        def _update_playlist():
            model = get_object_or_404(PlaylistModel, id=entity.id)
            model.name = entity.name
            model.description = entity.description
            model.is_public = entity.is_public
            model.save()
            return model
        
        model = await sync_to_async(_update_playlist)()
        return self.mapper.model_to_entity(model)
    
    async def delete(self, entity_id: UUID) -> bool:
        """Elimina una playlist (solo si no es default)"""
        self.logger.info(f"Deleting playlist: {entity_id}")
        
        def _delete_playlist():
            try:
                model = PlaylistModel.objects.get(id=entity_id)
                if model.is_default:
                    raise ValueError("No se puede eliminar una playlist por defecto")
                model.delete()
                return True
            except PlaylistModel.DoesNotExist:
                return False
        
        return await sync_to_async(_delete_playlist)()
    
    async def get_by_user_id(self, user_id: UUID) -> List[PlaylistEntity]:
        """Obtiene todas las playlists de un usuario"""
        self.logger.debug(f"Getting playlists for user: {user_id}")
        
        def _get_playlists():
            models = PlaylistModel.objects.filter(user_id=user_id).order_by('created_at')
            return list(models)
        
        models = await sync_to_async(_get_playlists)()
        return [self.mapper.model_to_entity(model) for model in models]
    
    async def get_default_playlist(self, user_id: UUID, name: str = "Favoritos") -> Optional[PlaylistEntity]:
        """Obtiene la playlist por defecto de un usuario (ej: Favoritos)"""
        self.logger.debug(f"Getting default playlist '{name}' for user: {user_id}")
        
        def _get_default():
            try:
                model = PlaylistModel.objects.get(
                    user_id=user_id,
                    name=name,
                    is_default=True
                )
                return model
            except PlaylistModel.DoesNotExist:
                return None
        
        model = await sync_to_async(_get_default)()
        return self.mapper.model_to_entity(model) if model else None
    
    async def create_default_playlist(self, user_id: UUID, name: str = "Favoritos") -> PlaylistEntity:
        """Crea la playlist por defecto para un usuario"""
        self.logger.info(f"Creating default playlist '{name}' for user: {user_id}")
        
        def _create_default():
            return PlaylistModel.objects.create(
                name=name,
                description=f"Tu playlist {name}",
                user_id=user_id,
                is_default=True,
                is_public=False
            )
        
        model = await sync_to_async(_create_default)()
        return self.mapper.model_to_entity(model)
    
    async def add_song_to_playlist(self, playlist_id: UUID, song_id: UUID, position: Optional[int] = None) -> PlaylistSongEntity:
        """Añade una canción a una playlist"""
        self.logger.info(f"Adding song {song_id} to playlist {playlist_id}")
        
        def _add_song():
            with transaction.atomic():
                # Si no se especifica posición, agregar al final
                if position is None:
                    last_position = PlaylistSongModel.objects.filter(
                        playlist_id=playlist_id
                    ).count()
                    position_to_use = last_position + 1
                else:
                    position_to_use = position
                    # Mover las canciones siguientes una posición hacia abajo
                    PlaylistSongModel.objects.filter(
                        playlist_id=playlist_id,
                        position__gte=position_to_use
                    ).update(position=models.F('position') + 1)
                
                # Verificar si la canción ya está en la playlist
                existing = PlaylistSongModel.objects.filter(
                    playlist_id=playlist_id,
                    song_id=song_id
                ).first()
                
                if existing:
                    raise ValueError("La canción ya está en esta playlist")
                
                playlist_song = PlaylistSongModel.objects.create(
                    playlist_id=playlist_id,
                    song_id=song_id,
                    position=position_to_use
                )
                return playlist_song
        
        from django.db import models
        model = await sync_to_async(_add_song)()
        
        return PlaylistSongEntity(
            id=model.id,
            playlist_id=model.playlist.id,
            song_id=model.song.id,
            position=model.position,
            added_at=model.added_at
        )
    
    async def remove_song_from_playlist(self, playlist_id: UUID, song_id: UUID) -> bool:
        """Remueve una canción de una playlist"""
        self.logger.info(f"Removing song {song_id} from playlist {playlist_id}")
        
        def _remove_song():
            with transaction.atomic():
                try:
                    playlist_song = PlaylistSongModel.objects.get(
                        playlist_id=playlist_id,
                        song_id=song_id
                    )
                    position = playlist_song.position
                    playlist_song.delete()
                    
                    # Mover las canciones siguientes una posición hacia arriba
                    PlaylistSongModel.objects.filter(
                        playlist_id=playlist_id,
                        position__gt=position
                    ).update(position=models.F('position') - 1)
                    
                    return True
                except PlaylistSongModel.DoesNotExist:
                    return False
        
        from django.db import models
        return await sync_to_async(_remove_song)()
    
    async def get_playlist_songs(self, playlist_id: UUID) -> List[PlaylistSongEntity]:
        """Obtiene todas las canciones de una playlist"""
        self.logger.debug(f"Getting songs for playlist: {playlist_id}")
        
        def _get_songs():
            models = PlaylistSongModel.objects.filter(
                playlist_id=playlist_id
            ).order_by('position')
            return list(models)
        
        models = await sync_to_async(_get_songs)()
        return [
            PlaylistSongEntity(
                id=model.id,
                playlist_id=model.playlist.id,
                song_id=model.song.id,
                position=model.position,
                added_at=model.added_at
            )
            for model in models
        ]
