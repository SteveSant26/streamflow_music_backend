from typing import Any, Dict

from apps.playlists.domain.entities import PlaylistEntity, PlaylistSongEntity
from apps.playlists.infrastructure.models import PlaylistModel, PlaylistSongModel
from common.interfaces.imapper.abstract_model_entity_mapper import AbstractEntityModelMapper


class PlaylistEntityModelMapper(AbstractEntityModelMapper[PlaylistEntity, PlaylistModel]):
    """Mapper entre PlaylistModel y PlaylistEntity"""
    
    def __init__(self):
        super().__init__()
    
    def model_to_entity(self, model: PlaylistModel) -> PlaylistEntity:
        """Convierte un PlaylistModel a PlaylistEntity"""
        self.logger.debug(f"Converting model to entity for playlist {model.id}")
        
        return PlaylistEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            user_id=model.user.id,
            is_default=model.is_default,
            is_public=model.is_public,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    def entity_to_model(self, entity: PlaylistEntity) -> PlaylistModel:
        """Convierte una PlaylistEntity a PlaylistModel"""
        self.logger.debug(f"Converting entity to model for playlist {entity.id}")
        
        from apps.user_profile.infrastructure.models import UserProfileModel
        
        return PlaylistModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            user_id=entity.user_id,
            is_default=entity.is_default,
            is_public=entity.is_public,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    def entity_to_model_data(self, entity: PlaylistEntity) -> Dict[str, Any]:
        """Convierte una PlaylistEntity a datos para PlaylistModel"""
        self.logger.debug(f"Converting entity to model data for playlist {entity.id}")
        
        return {
            "id": entity.id,
            "name": entity.name,
            "description": entity.description,
            "user_id": entity.user_id,
            "is_default": entity.is_default,
            "is_public": entity.is_public,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }


class PlaylistSongEntityModelMapper(AbstractEntityModelMapper[PlaylistSongEntity, PlaylistSongModel]):
    """Mapper entre PlaylistSongModel y PlaylistSongEntity"""
    
    def __init__(self):
        super().__init__()
    
    def model_to_entity(self, model: PlaylistSongModel) -> PlaylistSongEntity:
        """Convierte un PlaylistSongModel a PlaylistSongEntity"""
        self.logger.debug(f"Converting model to entity for playlist song {model.id}")
        
        return PlaylistSongEntity(
            id=model.id,
            playlist_id=model.playlist.id,
            song_id=model.song.id,
            position=model.position,
            added_at=model.added_at,
        )
    
    def entity_to_model(self, entity: PlaylistSongEntity) -> PlaylistSongModel:
        """Convierte una PlaylistSongEntity a PlaylistSongModel"""
        self.logger.debug(f"Converting entity to model for playlist song {entity.id}")
        
        return PlaylistSongModel(
            id=entity.id,
            playlist_id=entity.playlist_id,
            song_id=entity.song_id,
            position=entity.position,
            added_at=entity.added_at,
        )
    
    def entity_to_model_data(self, entity: PlaylistSongEntity) -> Dict[str, Any]:
        """Convierte una PlaylistSongEntity a datos para PlaylistSongModel"""
        self.logger.debug(f"Converting entity to model data for playlist song {entity.id}")
        
        return {
            "id": entity.id,
            "playlist_id": entity.playlist_id,
            "song_id": entity.song_id,
            "position": entity.position,
            "added_at": entity.added_at,
        }
