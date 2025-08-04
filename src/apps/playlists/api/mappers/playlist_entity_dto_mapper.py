from typing import List

from apps.playlists.api.dtos.playlist_dtos import (
    PlaylistResponseDTO,
    PlaylistSongResponseDTO,
)
from apps.playlists.domain.entities import PlaylistEntity, PlaylistSongEntity
from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper


class PlaylistEntityDtoMapper(AbstractEntityDtoMapper[PlaylistEntity, PlaylistResponseDTO]):
    """Mapper entre PlaylistEntity y PlaylistResponseDTO"""
    
    def __init__(self):
        super().__init__()
    
    def entity_to_dto(self, entity: PlaylistEntity) -> PlaylistResponseDTO:
        """Convierte una PlaylistEntity a PlaylistResponseDTO"""
        self.logger.debug(f"Converting entity to DTO for playlist {entity.id}")
        
        return PlaylistResponseDTO(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            user_id=entity.user_id,
            is_default=entity.is_default,
            is_public=entity.is_public,
            total_songs=0,  # Se calculará en el repositorio o caso de uso
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    def dto_to_entity(self, dto: PlaylistResponseDTO) -> PlaylistEntity:
        """Convierte un PlaylistResponseDTO a PlaylistEntity"""
        self.logger.debug(f"Converting DTO to entity for playlist {dto.id}")
        
        return PlaylistEntity(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            user_id=dto.user_id,
            is_default=dto.is_default,
            is_public=dto.is_public,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
    
    def entities_to_dtos(self, entities: List[PlaylistEntity]) -> List[PlaylistResponseDTO]:
        """Convierte una lista de PlaylistEntity a PlaylistResponseDTO"""
        return [self.entity_to_dto(entity) for entity in entities]


class PlaylistSongEntityDtoMapper(AbstractEntityDtoMapper[PlaylistSongEntity, PlaylistSongResponseDTO]):
    """Mapper entre PlaylistSongEntity y PlaylistSongResponseDTO"""
    
    def __init__(self):
        super().__init__()
    
    def entity_to_dto(self, entity: PlaylistSongEntity) -> PlaylistSongResponseDTO:
        """Convierte una PlaylistSongEntity a PlaylistSongResponseDTO"""
        self.logger.debug(f"Converting entity to DTO for playlist song {entity.id}")
        
        # Nota: La información de la canción (title, artist_name, etc.) 
        # debe ser añadida por el caso de uso que tiene acceso al repositorio de canciones
        return PlaylistSongResponseDTO(
            id=entity.id,
            title="",  # Se llenará en el caso de uso
            artist_name=None,
            album_name=None,
            duration_seconds=0,
            thumbnail_url=None,
            position=entity.position,
            added_at=entity.added_at,
        )
    
    def dto_to_entity(self, dto: PlaylistSongResponseDTO) -> PlaylistSongEntity:
        """Convierte un PlaylistSongResponseDTO a PlaylistSongEntity"""
        self.logger.debug(f"Converting DTO to entity for playlist song {dto.id}")
        
        return PlaylistSongEntity(
            id=dto.id,
            playlist_id=None,  # Se debe establecer externamente
            song_id=None,  # Se debe establecer externamente
            position=dto.position,
            added_at=dto.added_at,
        )
    
    def entities_to_dtos(self, entities: List[PlaylistSongEntity]) -> List[PlaylistSongResponseDTO]:
        """Convierte una lista de PlaylistSongEntity a PlaylistSongResponseDTO"""
        return [self.entity_to_dto(entity) for entity in entities]
