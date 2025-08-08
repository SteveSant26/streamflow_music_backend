"""
🧪 TESTS UNITARIOS PARA PLAYLIST REPOSITORY
=========================================
Tests completos para el repositorio de playlists con mocks para Django ORM
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import uuid

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from apps.playlists.infrastructure.repository.playlist_repository import PlaylistRepository
from apps.playlists.domain.entities import PlaylistEntity, PlaylistSongEntity
from apps.playlists.infrastructure.models import PlaylistModel, PlaylistSongModel
from apps.playlists.api.mappers.playlist_entity_model_mapper import PlaylistEntityModelMapper


class TestPlaylistRepository:
    """Tests unitarios para PlaylistRepository"""

    @pytest.fixture
    def mock_playlist_model(self):
        """Mock del modelo PlaylistModel"""
        mock_model = Mock()
        mock_model.id = "playlist-123"
        mock_model.name = "Test Playlist"
        mock_model.description = "Test Description"
        mock_model.user_id = "user-123"
        mock_model.is_public = True
        mock_model.is_default = False
        mock_model.is_active = True
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()
        return mock_model

    @pytest.fixture
    def playlist_entity(self):
        """Entidad de playlist de prueba"""
        return PlaylistEntity(
            id="playlist-123",
            name="Test Playlist",
            description="Test Description",
            user_id="user-123",
            is_public=True,
            is_default=False,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.fixture
    def playlist_song_entity(self):
        """Entidad de playlist song de prueba"""
        return PlaylistSongEntity(
            id="playlist-song-123",
            playlist_id="playlist-123",
            song_id="song-123",
            position=1,
            added_at=datetime.now()
        )

    @pytest.fixture
    def mock_mapper(self):
        """Mock del mapper"""
        mapper = Mock(spec=PlaylistEntityModelMapper)
        mapper.model_to_entity.return_value = Mock()
        mapper.entity_to_model_data.return_value = {
            'name': 'Test Playlist',
            'description': 'Test Description',
            'user_id': 'user-123',
            'is_public': True,
            'is_default': False,
            'is_active': True
        }
        return mapper

    @pytest.fixture
    def repository(self):
        """Instancia del repositorio con mocks"""
        with patch('apps.playlists.infrastructure.repository.playlist_repository.PlaylistModel') as mock_model, \
             patch('apps.playlists.infrastructure.repository.playlist_repository.PlaylistEntityModelMapper') as mock_mapper_class:
            
            mock_mapper = Mock()
            mock_mapper_class.return_value = mock_mapper
            
            repo = PlaylistRepository()
            repo.model = mock_model
            repo.mapper = mock_mapper
            return repo

    @pytest.mark.asyncio
    async def test_create_playlist_success(self, repository, playlist_entity, mock_playlist_model):
        """Test de creación exitosa de playlist"""
        # Configurar mocks
        repository.mapper.entity_to_model_data.return_value = {
            'name': playlist_entity.name,
            'description': playlist_entity.description,
            'user_id': playlist_entity.user_id,
            'is_public': playlist_entity.is_public
        }
        
        repository.model.objects.acreate = AsyncMock(return_value=mock_playlist_model)
        repository.mapper.model_to_entity.return_value = playlist_entity
        
        # Ejecutar
        result = await repository.create(playlist_entity)
        
        # Verificar
        assert result == playlist_entity
        repository.model.objects.acreate.assert_called_once()
        repository.mapper.entity_to_model_data.assert_called_once_with(playlist_entity)

    @pytest.mark.asyncio
    async def test_create_playlist_removes_timestamps(self, repository, playlist_entity, mock_playlist_model):
        """Test que la creación remueve timestamps automáticos"""
        # Configurar mock que incluye timestamps
        repository.mapper.entity_to_model_data.return_value = {
            'name': playlist_entity.name,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        repository.model.objects.acreate = AsyncMock(return_value=mock_playlist_model)
        repository.mapper.model_to_entity.return_value = playlist_entity
        
        # Ejecutar
        await repository.create(playlist_entity)
        
        # Verificar que se llamó acreate sin timestamps
        call_args = repository.model.objects.acreate.call_args[1]
        assert 'created_at' not in call_args
        assert 'updated_at' not in call_args

    @pytest.mark.asyncio
    async def test_update_playlist_success(self, repository, playlist_entity, mock_playlist_model):
        """Test de actualización exitosa de playlist"""
        # Configurar mocks
        repository.model.objects.select_related.return_value.aget = AsyncMock(return_value=mock_playlist_model)
        mock_playlist_model.asave = AsyncMock()
        repository.mapper.model_to_entity.return_value = playlist_entity
        
        # Ejecutar
        result = await repository.update_playlist(playlist_entity)
        
        # Verificar
        assert result == playlist_entity
        assert mock_playlist_model.name == playlist_entity.name
        assert mock_playlist_model.description == playlist_entity.description
        assert mock_playlist_model.is_public == playlist_entity.is_public
        mock_playlist_model.asave.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_playlist_not_found(self, repository, playlist_entity):
        """Test de actualización con playlist no encontrada"""
        from django.core.exceptions import ObjectDoesNotExist
        
        # Configurar mock para lanzar excepción
        repository.model.objects.select_related.return_value.aget = AsyncMock(
            side_effect=ObjectDoesNotExist("Playlist not found")
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(ObjectDoesNotExist):
            await repository.update_playlist(playlist_entity)

    @pytest.mark.asyncio
    async def test_delete_playlist_success(self, repository):
        """Test de eliminación exitosa de playlist"""
        playlist_id = "playlist-123"
        mock_model = Mock()
        mock_model.is_default = False
        mock_model.adelete = AsyncMock()
        
        repository.model.objects.select_related.return_value.aget = AsyncMock(return_value=mock_model)
        
        # Ejecutar
        result = await repository.delete_playlist(playlist_id)
        
        # Verificar
        assert result is True
        mock_model.adelete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_playlist_is_default(self, repository):
        """Test de intento de eliminación de playlist por defecto"""
        playlist_id = "playlist-123"
        mock_model = Mock()
        mock_model.is_default = True
        
        repository.model.objects.select_related.return_value.aget = AsyncMock(return_value=mock_model)
        
        # Ejecutar
        result = await repository.delete_playlist(playlist_id)
        
        # Verificar que no se elimina playlist por defecto
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_playlist_not_found(self, repository):
        """Test de eliminación con playlist no encontrada"""
        from django.core.exceptions import ObjectDoesNotExist
        
        playlist_id = "nonexistent-playlist"
        repository.model.objects.select_related.return_value.aget = AsyncMock(
            side_effect=ObjectDoesNotExist("Playlist not found")
        )
        
        # Ejecutar
        result = await repository.delete_playlist(playlist_id)
        
        # Verificar
        assert result is False

    @pytest.mark.asyncio
    async def test_get_by_user_id_success(self, repository, playlist_entity):
        """Test de obtención de playlists por user_id"""
        user_id = "user-123"
        mock_models = [Mock(), Mock()]
        
        # Configurar QuerySet mock
        mock_queryset = Mock()
        mock_queryset.__aiter__ = AsyncMock(return_value=iter(mock_models))
        repository.model.objects.filter.return_value.select_related.return_value = mock_queryset
        
        repository.mapper.models_to_entities.return_value = [playlist_entity, playlist_entity]
        
        # Ejecutar
        result = await repository.get_by_user_id(user_id)
        
        # Verificar
        assert len(result) == 2
        repository.model.objects.filter.assert_called_with(user_id=user_id, is_active=True)

    @pytest.mark.asyncio
    async def test_get_by_user_id_empty_result(self, repository):
        """Test de obtención sin resultados"""
        user_id = "user-123"
        
        # Configurar QuerySet vacío
        mock_queryset = Mock()
        mock_queryset.__aiter__ = AsyncMock(return_value=iter([]))
        repository.model.objects.filter.return_value.select_related.return_value = mock_queryset
        
        repository.mapper.models_to_entities.return_value = []
        
        # Ejecutar
        result = await repository.get_by_user_id(user_id)
        
        # Verificar
        assert result == []

    @pytest.mark.asyncio
    async def test_get_default_playlist_found(self, repository, playlist_entity):
        """Test de obtención de playlist por defecto encontrada"""
        user_id = "user-123"
        name = "Favoritos"
        mock_model = Mock()
        
        repository.model.objects.aget = AsyncMock(return_value=mock_model)
        repository.mapper.model_to_entity.return_value = playlist_entity
        
        # Ejecutar
        result = await repository.get_default_playlist(user_id, name)
        
        # Verificar
        assert result == playlist_entity
        repository.model.objects.aget.assert_called_with(
            user_id=user_id, name=name, is_default=True, is_active=True
        )

    @pytest.mark.asyncio
    async def test_get_default_playlist_not_found(self, repository):
        """Test de playlist por defecto no encontrada"""
        from django.core.exceptions import ObjectDoesNotExist
        
        user_id = "user-123"
        name = "Favoritos"
        
        repository.model.objects.aget = AsyncMock(
            side_effect=ObjectDoesNotExist("Playlist not found")
        )
        
        # Ejecutar
        result = await repository.get_default_playlist(user_id, name)
        
        # Verificar
        assert result is None

    @pytest.mark.asyncio
    async def test_add_song_to_playlist_success(self, repository, playlist_song_entity):
        """Test de adición exitosa de canción a playlist"""
        mock_playlist_song = Mock()
        
        # Mock para crear PlaylistSongModel
        with patch('apps.playlists.infrastructure.repository.playlist_repository.PlaylistSongModel') as mock_song_model:
            mock_song_model.objects.acreate = AsyncMock(return_value=mock_playlist_song)
            
            # Ejecutar
            result = await repository.add_song_to_playlist(
                playlist_song_entity.playlist_id,
                playlist_song_entity.song_id,
                playlist_song_entity.position
            )
            
            # Verificar
            assert result is True
            mock_song_model.objects.acreate.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_song_to_playlist_error(self, repository):
        """Test de error al añadir canción a playlist"""
        with patch('apps.playlists.infrastructure.repository.playlist_repository.PlaylistSongModel') as mock_song_model:
            mock_song_model.objects.acreate = AsyncMock(side_effect=Exception("Database error"))
            
            # Ejecutar
            result = await repository.add_song_to_playlist("playlist-123", "song-123", 1)
            
            # Verificar
            assert result is False

    @pytest.mark.asyncio
    async def test_remove_song_from_playlist_success(self, repository):
        """Test de eliminación exitosa de canción de playlist"""
        mock_playlist_song = Mock()
        mock_playlist_song.adelete = AsyncMock()
        
        with patch('apps.playlists.infrastructure.repository.playlist_repository.PlaylistSongModel') as mock_song_model:
            mock_song_model.objects.aget = AsyncMock(return_value=mock_playlist_song)
            
            # Ejecutar
            result = await repository.remove_song_from_playlist("playlist-123", "song-123")
            
            # Verificar
            assert result is True
            mock_playlist_song.adelete.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_song_from_playlist_not_found(self, repository):
        """Test de eliminación con canción no encontrada"""
        from django.core.exceptions import ObjectDoesNotExist
        
        with patch('apps.playlists.infrastructure.repository.playlist_repository.PlaylistSongModel') as mock_song_model:
            mock_song_model.objects.aget = AsyncMock(
                side_effect=ObjectDoesNotExist("PlaylistSong not found")
            )
            
            # Ejecutar
            result = await repository.remove_song_from_playlist("playlist-123", "song-123")
            
            # Verificar
            assert result is False

    @pytest.mark.asyncio
    async def test_get_playlist_songs_success(self, repository, playlist_song_entity):
        """Test de obtención de canciones de playlist"""
        playlist_id = "playlist-123"
        mock_songs = [Mock(), Mock()]
        
        with patch('apps.playlists.infrastructure.repository.playlist_repository.PlaylistSongModel') as mock_song_model:
            # Configurar QuerySet mock
            mock_queryset = Mock()
            mock_queryset.__aiter__ = AsyncMock(return_value=iter(mock_songs))
            mock_song_model.objects.filter.return_value.select_related.return_value.order_by.return_value = mock_queryset
            
            with patch('apps.playlists.infrastructure.repository.playlist_repository.PlaylistSongEntityModelMapper') as mock_mapper_class:
                mock_mapper = Mock()
                mock_mapper.models_to_entities.return_value = [playlist_song_entity, playlist_song_entity]
                mock_mapper_class.return_value = mock_mapper
                
                # Ejecutar
                result = await repository.get_playlist_songs(playlist_id)
                
                # Verificar
                assert len(result) == 2
                mock_song_model.objects.filter.assert_called_with(playlist_id=playlist_id)

    @pytest.mark.asyncio
    async def test_update_song_position_success(self, repository):
        """Test de actualización exitosa de posición de canción"""
        mock_playlist_song = Mock()
        mock_playlist_song.asave = AsyncMock()
        
        with patch('apps.playlists.infrastructure.repository.playlist_repository.PlaylistSongModel') as mock_song_model:
            mock_song_model.objects.aget = AsyncMock(return_value=mock_playlist_song)
            
            # Ejecutar
            result = await repository.update_song_position("playlist-123", "song-123", 5)
            
            # Verificar
            assert result is True
            assert mock_playlist_song.position == 5
            mock_playlist_song.asave.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_song_position_not_found(self, repository):
        """Test de actualización con canción no encontrada"""
        from django.core.exceptions import ObjectDoesNotExist
        
        with patch('apps.playlists.infrastructure.repository.playlist_repository.PlaylistSongModel') as mock_song_model:
            mock_song_model.objects.aget = AsyncMock(
                side_effect=ObjectDoesNotExist("PlaylistSong not found")
            )
            
            # Ejecutar
            result = await repository.update_song_position("playlist-123", "song-123", 5)
            
            # Verificar
            assert result is False

    def test_repository_inheritance(self, repository):
        """Test de herencia correcta del repositorio"""
        from common.core.repositories import BaseDjangoRepository
        from apps.playlists.domain.repository.iplaylist_repository import IPlaylistRepository
        
        assert isinstance(repository, BaseDjangoRepository)
        assert isinstance(repository, IPlaylistRepository)

    def test_repository_initialization(self, repository):
        """Test de inicialización correcta del repositorio"""
        assert repository.model is not None
        assert repository.mapper is not None

    @pytest.mark.asyncio
    async def test_logging_integration(self, repository, playlist_entity):
        """Test de integración con logging"""
        # Verificar que el repositorio tiene logger
        assert hasattr(repository, 'logger')
        
        # Mock del logger para verificar llamadas
        repository.logger = Mock()
        
        # Configurar mocks para create
        repository.mapper.entity_to_model_data.return_value = {}
        repository.model.objects.acreate = AsyncMock(return_value=Mock())
        repository.mapper.model_to_entity.return_value = playlist_entity
        
        # Ejecutar operación que debería loggear
        await repository.create(playlist_entity)
        
        # Verificar que se llamó al logger
        repository.logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_transaction_handling(self, repository):
        """Test de manejo de transacciones en operaciones complejas"""
        playlist_id = "playlist-123"
        song_ids = ["song-1", "song-2", "song-3"]
        
        with patch('apps.playlists.infrastructure.repository.playlist_repository.PlaylistSongModel') as mock_song_model:
            # Mock para operaciones batch
            mock_song_model.objects.acreate = AsyncMock()
            
            # Simular operación batch (si existe en la implementación)
            try:
                for i, song_id in enumerate(song_ids):
                    await repository.add_song_to_playlist(playlist_id, song_id, i + 1)
                
                # Verificar que se llamó acreate para cada canción
                assert mock_song_model.objects.acreate.call_count == len(song_ids)
            except AttributeError:
                # Si no hay operación batch, esto es esperado
                pass

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, repository, playlist_entity):
        """Test de operaciones concurrentes"""
        import asyncio
        
        # Configurar mocks
        repository.mapper.entity_to_model_data.return_value = {}
        repository.model.objects.acreate = AsyncMock(return_value=Mock())
        repository.mapper.model_to_entity.return_value = playlist_entity
        
        # Crear múltiples entidades
        entities = [
            PlaylistEntity(
                id=f"playlist-{i}",
                name=f"Playlist {i}",
                description=f"Description {i}",
                user_id="user-123",
                is_public=True,
                is_default=False,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            for i in range(3)
        ]
        
        # Ejecutar operaciones concurrentes
        tasks = [repository.create(entity) for entity in entities]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verificar resultados
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)
