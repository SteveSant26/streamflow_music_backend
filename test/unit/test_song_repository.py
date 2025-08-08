"""
🧪 TESTS UNITARIOS PARA SONG REPOSITORY
====================================
Tests completos para el repositorio de canciones con mocks para Django ORM
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
import uuid

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from apps.songs.infrastructure.repository.song_repository import SongRepository
from apps.songs.domain.entities import SongEntity
from apps.songs.infrastructure.models.song_model import SongModel
from apps.songs.api.mappers import SongEntityModelMapper


class TestSongRepository:
    """Tests unitarios para SongRepository"""

    @pytest.fixture
    def mock_song_model(self):
        """Mock del modelo SongModel"""
        mock_model = Mock()
        mock_model.id = "song-123"
        mock_model.title = "Test Song"
        mock_model.album_id = "album-123"
        mock_model.artist_id = "artist-123"
        mock_model.duration_seconds = 180
        mock_model.file_url = "https://example.com/song.mp3"
        mock_model.thumbnail_url = "https://example.com/thumb.jpg"
        mock_model.play_count = 100
        mock_model.is_active = True
        mock_model.created_at = datetime.now()
        mock_model.updated_at = datetime.now()
        mock_model.asave = AsyncMock()
        return mock_model

    @pytest.fixture
    def song_entity(self):
        """Entidad de canción de prueba"""
        return SongEntity(
            id="song-123",
            title="Test Song",
            album_id="album-123",
            artist_id="artist-123",
            genre_ids=["genre-1", "genre-2"],
            duration_seconds=180,
            file_url="https://example.com/song.mp3",
            thumbnail_url="https://example.com/thumb.jpg",
            play_count=100,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.fixture
    def mock_mapper(self):
        """Mock del mapper de canciones"""
        mapper = Mock(spec=SongEntityModelMapper)
        mapper.model_to_entity.return_value = Mock()
        mapper.entity_to_model_data.return_value = {
            'title': 'Test Song',
            'album_id': 'album-123',
            'artist_id': 'artist-123',
            'duration_seconds': 180,
            'file_url': 'https://example.com/song.mp3',
            'is_active': True
        }
        mapper.set_entity_genres_to_model = AsyncMock()
        return mapper

    @pytest.fixture
    def repository(self):
        """Instancia del repositorio con mocks"""
        with patch('apps.songs.infrastructure.repository.song_repository.SongModel') as mock_model, \
             patch('apps.songs.infrastructure.repository.song_repository.SongEntityModelMapper') as mock_mapper_class:
            
            mock_mapper = Mock()
            mock_mapper_class.return_value = mock_mapper
            
            repo = SongRepository()
            repo.model_class = mock_model
            repo.mapper = mock_mapper
            return repo

    @pytest.mark.asyncio
    async def test_save_new_song_success(self, repository, song_entity, mock_song_model):
        """Test de guardado exitoso de nueva canción"""
        # Configurar mocks
        song_entity.id = None  # Nueva canción sin ID
        repository.mapper.entity_to_model_data.return_value = {
            'title': song_entity.title,
            'album_id': song_entity.album_id,
            'artist_id': song_entity.artist_id,
            'duration_seconds': song_entity.duration_seconds
        }
        
        repository.model_class.objects.acreate = AsyncMock(return_value=mock_song_model)
        repository.mapper.model_to_entity.return_value = song_entity
        repository.mapper.set_entity_genres_to_model = AsyncMock()
        
        # Ejecutar
        result = await repository.save(song_entity)
        
        # Verificar
        assert result == song_entity
        repository.model_class.objects.acreate.assert_called_once()
        repository.mapper.set_entity_genres_to_model.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_existing_song_success(self, repository, song_entity, mock_song_model):
        """Test de actualización exitosa de canción existente"""
        # Configurar mocks
        repository.mapper.entity_to_model_data.return_value = {
            'title': song_entity.title,
            'album_id': song_entity.album_id,
            'artist_id': song_entity.artist_id,
            'duration_seconds': song_entity.duration_seconds
        }
        
        repository.model_class.objects.aget = AsyncMock(return_value=mock_song_model)
        repository.mapper.model_to_entity.return_value = song_entity
        repository.mapper.set_entity_genres_to_model = AsyncMock()
        
        # Ejecutar
        result = await repository.save(song_entity)
        
        # Verificar
        assert result == song_entity
        repository.model_class.objects.aget.assert_called_once_with(id=song_entity.id)
        mock_song_model.asave.assert_called_once()
        repository.mapper.set_entity_genres_to_model.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_existing_song_not_found_creates_new(self, repository, song_entity, mock_song_model):
        """Test de creación cuando canción existente no se encuentra"""
        # Configurar mocks
        repository.mapper.entity_to_model_data.return_value = {
            'title': song_entity.title,
            'album_id': song_entity.album_id
        }
        
        # Mock para que aget lance DoesNotExist
        repository.model_class.DoesNotExist = Exception
        repository.model_class.objects.aget = AsyncMock(side_effect=repository.model_class.DoesNotExist)
        repository.model_class.objects.acreate = AsyncMock(return_value=mock_song_model)
        repository.mapper.model_to_entity.return_value = song_entity
        repository.mapper.set_entity_genres_to_model = AsyncMock()
        
        # Ejecutar
        result = await repository.save(song_entity)
        
        # Verificar
        assert result == song_entity
        repository.model_class.objects.acreate.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_without_genres(self, repository, song_entity, mock_song_model):
        """Test de guardado sin géneros"""
        # Configurar entidad sin géneros
        song_entity.genre_ids = None
        
        repository.mapper.entity_to_model_data.return_value = {'title': song_entity.title}
        repository.model_class.objects.acreate = AsyncMock(return_value=mock_song_model)
        repository.mapper.model_to_entity.return_value = song_entity
        repository.mapper.set_entity_genres_to_model = AsyncMock()
        
        # Ejecutar
        result = await repository.save(song_entity)
        
        # Verificar que no se intenta configurar géneros
        repository.mapper.set_entity_genres_to_model.assert_not_called()

    @pytest.mark.asyncio
    async def test_find_by_artist_id_success(self, repository, song_entity):
        """Test de búsqueda exitosa por artist_id"""
        artist_id = "artist-123"
        mock_songs = [Mock(), Mock()]
        
        # Configurar QuerySet mock
        mock_queryset = Mock()
        mock_queryset.__aiter__ = AsyncMock(return_value=iter(mock_songs))
        repository.model_class.objects.filter.return_value = mock_queryset
        
        repository.mapper.models_to_entities.return_value = [song_entity, song_entity]
        
        # Ejecutar
        result = await repository.find_by_artist_id(artist_id)
        
        # Verificar
        assert len(result) == 2
        repository.model_class.objects.filter.assert_called_with(artist_id=artist_id, is_active=True)

    @pytest.mark.asyncio
    async def test_find_by_artist_id_empty_result(self, repository):
        """Test de búsqueda sin resultados por artist_id"""
        artist_id = "nonexistent-artist"
        
        # Configurar QuerySet vacío
        mock_queryset = Mock()
        mock_queryset.__aiter__ = AsyncMock(return_value=iter([]))
        repository.model_class.objects.filter.return_value = mock_queryset
        
        repository.mapper.models_to_entities.return_value = []
        
        # Ejecutar
        result = await repository.find_by_artist_id(artist_id)
        
        # Verificar
        assert result == []

    @pytest.mark.asyncio
    async def test_find_by_album_id_success(self, repository, song_entity):
        """Test de búsqueda exitosa por album_id"""
        album_id = "album-123"
        mock_songs = [Mock(), Mock(), Mock()]
        
        # Configurar QuerySet mock
        mock_queryset = Mock()
        mock_queryset.__aiter__ = AsyncMock(return_value=iter(mock_songs))
        repository.model_class.objects.filter.return_value = mock_queryset
        
        repository.mapper.models_to_entities.return_value = [song_entity] * 3
        
        # Ejecutar
        result = await repository.find_by_album_id(album_id)
        
        # Verificar
        assert len(result) == 3
        repository.model_class.objects.filter.assert_called_with(album_id=album_id, is_active=True)

    @pytest.mark.asyncio
    async def test_search_songs_by_title_success(self, repository, song_entity):
        """Test de búsqueda exitosa por título"""
        title = "Test Song"
        mock_songs = [Mock()]
        
        # Configurar QuerySet mock con filtro icontains
        mock_queryset = Mock()
        mock_queryset.__aiter__ = AsyncMock(return_value=iter(mock_songs))
        repository.model_class.objects.filter.return_value = mock_queryset
        
        repository.mapper.models_to_entities.return_value = [song_entity]
        
        # Ejecutar
        result = await repository.search_songs_by_title(title)
        
        # Verificar
        assert len(result) == 1
        # Verificar que se usó icontains para búsqueda parcial
        filter_call = repository.model_class.objects.filter.call_args
        assert any('title__icontains' in str(arg) for arg in filter_call)

    @pytest.mark.asyncio
    async def test_search_songs_by_title_empty_result(self, repository):
        """Test de búsqueda sin resultados por título"""
        title = "Nonexistent Song"
        
        # Configurar QuerySet vacío
        mock_queryset = Mock()
        mock_queryset.__aiter__ = AsyncMock(return_value=iter([]))
        repository.model_class.objects.filter.return_value = mock_queryset
        
        repository.mapper.models_to_entities.return_value = []
        
        # Ejecutar
        result = await repository.search_songs_by_title(title)
        
        # Verificar
        assert result == []

    @pytest.mark.asyncio
    async def test_get_popular_songs_success(self, repository, song_entity):
        """Test de obtención exitosa de canciones populares"""
        limit = 10
        mock_songs = [Mock() for _ in range(limit)]
        
        # Configurar QuerySet mock con order_by
        mock_queryset = Mock()
        mock_queryset.__aiter__ = AsyncMock(return_value=iter(mock_songs))
        
        # Configurar cadena de métodos del QuerySet
        repository.model_class.objects.filter.return_value.order_by.return_value.__getitem__.return_value = mock_queryset
        
        repository.mapper.models_to_entities.return_value = [song_entity] * limit
        
        # Ejecutar
        result = await repository.get_popular_songs(limit)
        
        # Verificar
        assert len(result) == limit
        repository.model_class.objects.filter.assert_called_with(is_active=True)

    @pytest.mark.asyncio
    async def test_get_recent_songs_success(self, repository, song_entity):
        """Test de obtención exitosa de canciones recientes"""
        limit = 5
        mock_songs = [Mock() for _ in range(limit)]
        
        # Configurar QuerySet mock
        mock_queryset = Mock()
        mock_queryset.__aiter__ = AsyncMock(return_value=iter(mock_songs))
        
        # Configurar cadena de métodos del QuerySet
        repository.model_class.objects.filter.return_value.order_by.return_value.__getitem__.return_value = mock_queryset
        
        repository.mapper.models_to_entities.return_value = [song_entity] * limit
        
        # Ejecutar
        result = await repository.get_recent_songs(limit)
        
        # Verificar
        assert len(result) == limit
        repository.model_class.objects.filter.assert_called_with(is_active=True)

    @pytest.mark.asyncio
    async def test_update_play_count_success(self, repository, mock_song_model):
        """Test de actualización exitosa del contador de reproducciones"""
        song_id = "song-123"
        initial_count = mock_song_model.play_count
        
        repository.model_class.objects.aget = AsyncMock(return_value=mock_song_model)
        
        # Ejecutar
        result = await repository.update_play_count(song_id)
        
        # Verificar
        assert result is True
        assert mock_song_model.play_count == initial_count + 1
        mock_song_model.asave.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_play_count_song_not_found(self, repository):
        """Test de actualización con canción no encontrada"""
        song_id = "nonexistent-song"
        
        repository.model_class.DoesNotExist = Exception
        repository.model_class.objects.aget = AsyncMock(side_effect=repository.model_class.DoesNotExist)
        
        # Ejecutar
        result = await repository.update_play_count(song_id)
        
        # Verificar
        assert result is False

    @pytest.mark.asyncio
    async def test_deactivate_song_success(self, repository, mock_song_model):
        """Test de desactivación exitosa de canción"""
        song_id = "song-123"
        mock_song_model.is_active = True
        
        repository.model_class.objects.aget = AsyncMock(return_value=mock_song_model)
        
        # Ejecutar
        result = await repository.deactivate_song(song_id)
        
        # Verificar
        assert result is True
        assert mock_song_model.is_active is False
        mock_song_model.asave.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_song_not_found(self, repository):
        """Test de desactivación con canción no encontrada"""
        song_id = "nonexistent-song"
        
        repository.model_class.DoesNotExist = Exception
        repository.model_class.objects.aget = AsyncMock(side_effect=repository.model_class.DoesNotExist)
        
        # Ejecutar
        result = await repository.deactivate_song(song_id)
        
        # Verificar
        assert result is False

    @pytest.mark.asyncio
    async def test_get_songs_by_genre_success(self, repository, song_entity):
        """Test de obtención de canciones por género"""
        genre_id = "genre-123"
        mock_songs = [Mock(), Mock()]
        
        # Configurar QuerySet mock para filtro de many-to-many
        mock_queryset = Mock()
        mock_queryset.__aiter__ = AsyncMock(return_value=iter(mock_songs))
        repository.model_class.objects.filter.return_value = mock_queryset
        
        repository.mapper.models_to_entities.return_value = [song_entity, song_entity]
        
        # Ejecutar
        result = await repository.get_songs_by_genre(genre_id)
        
        # Verificar
        assert len(result) == 2
        # Verificar que se filtró por genre
        filter_call = repository.model_class.objects.filter.call_args
        assert any('genres' in str(arg) for arg in filter_call)

    def test_repository_inheritance(self, repository):
        """Test de herencia correcta del repositorio"""
        from common.core import BaseDjangoRepository
        from apps.songs.domain.repository.Isong_repository import ISongRepository
        
        assert isinstance(repository, BaseDjangoRepository)
        assert isinstance(repository, ISongRepository)

    def test_repository_initialization(self, repository):
        """Test de inicialización correcta del repositorio"""
        assert repository.model_class is not None
        assert repository.mapper is not None

    @pytest.mark.asyncio
    async def test_logging_integration(self, repository, song_entity):
        """Test de integración con logging"""
        # Verificar que el repositorio tiene logger
        assert hasattr(repository, 'logger')
        
        # Mock del logger para verificar llamadas
        repository.logger = Mock()
        
        # Configurar mocks para save
        repository.mapper.entity_to_model_data.return_value = {}
        repository.model_class.objects.acreate = AsyncMock(return_value=Mock())
        repository.mapper.model_to_entity.return_value = song_entity
        repository.mapper.set_entity_genres_to_model = AsyncMock()
        
        song_entity.id = None  # Nueva canción
        
        # Ejecutar operación que debería loggear
        await repository.save(song_entity)
        
        # Verificar que se llamó al logger
        repository.logger.debug.assert_called()

    @pytest.mark.asyncio
    async def test_genre_assignment_error_handling(self, repository, song_entity, mock_song_model):
        """Test de manejo de errores en asignación de géneros"""
        # Configurar mocks
        repository.mapper.entity_to_model_data.return_value = {'title': song_entity.title}
        repository.model_class.objects.acreate = AsyncMock(return_value=mock_song_model)
        repository.mapper.model_to_entity.return_value = song_entity
        
        # Configurar error en asignación de géneros
        repository.mapper.set_entity_genres_to_model = AsyncMock(side_effect=Exception("Genre error"))
        
        # Ejecutar y verificar que no falla completamente
        with pytest.raises(Exception, match="Genre error"):
            await repository.save(song_entity)

    @pytest.mark.asyncio
    async def test_complex_search_query(self, repository, song_entity):
        """Test de consulta de búsqueda compleja"""
        # Simular búsqueda con múltiples criterios
        mock_queryset = Mock()
        mock_queryset.__aiter__ = AsyncMock(return_value=iter([Mock()]))
        
        # Configurar Q objects para búsqueda compleja
        with patch('apps.songs.infrastructure.repository.song_repository.Q') as mock_q:
            repository.model_class.objects.filter.return_value = mock_queryset
            repository.mapper.models_to_entities.return_value = [song_entity]
            
            # Ejecutar búsqueda por título (simulando búsqueda compleja)
            result = await repository.search_songs_by_title("test")
            
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_concurrent_updates(self, repository, song_entity):
        """Test de actualizaciones concurrentes"""
        import asyncio
        
        mock_song_model = Mock()
        mock_song_model.asave = AsyncMock()
        mock_song_model.play_count = 0
        
        repository.model_class.objects.aget = AsyncMock(return_value=mock_song_model)
        
        # Ejecutar múltiples actualizaciones concurrentes
        tasks = [repository.update_play_count("song-123") for _ in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verificar resultados
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception) or result is True

    @pytest.mark.asyncio
    async def test_batch_operations(self, repository, song_entity):
        """Test de operaciones en lote"""
        # Simular guardado de múltiples canciones
        entities = []
        for i in range(3):
            entity = SongEntity(
                id=None,  # Nuevas canciones
                title=f"Test Song {i}",
                album_id="album-123",
                artist_id="artist-123",
                duration_seconds=180,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            entities.append(entity)
        
        # Configurar mocks
        repository.mapper.entity_to_model_data.return_value = {}
        repository.model_class.objects.acreate = AsyncMock(return_value=Mock())
        repository.mapper.model_to_entity.return_value = song_entity
        repository.mapper.set_entity_genres_to_model = AsyncMock()
        
        # Ejecutar operaciones en lote
        results = []
        for entity in entities:
            result = await repository.save(entity)
            results.append(result)
        
        # Verificar
        assert len(results) == 3
        assert repository.model_class.objects.acreate.call_count == 3
