"""
🧪 TESTS UNITARIOS PARA YOUTUBE SERVICE
=====================================
Tests completos para el servicio de YouTube con mocks para dependencias externas
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from googleapiclient.errors import HttpError
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from common.adapters.media.youtube_service import YouTubeAPIService
from common.types.media_types import YouTubeServiceConfig, YouTubeVideoInfo, SearchOptions
from common.utils.validators import TextCleaner
from common.utils.music_metadata_extractor import MusicMetadataExtractor
from common.utils.retry_manager import RetryManager, CircuitBreaker


class TestYouTubeAPIService:
    """Tests unitarios para YouTubeAPIService"""

    @pytest.fixture
    def mock_settings(self):
        """Mock de Django settings"""
        return {
            'YOUTUBE_API_KEY': 'test_api_key',
            'YOUTUBE_API_SERVICE_NAME': 'youtube',
            'YOUTUBE_API_VERSION': 'v3'
        }

    @pytest.fixture
    def youtube_config(self):
        """Configuración de prueba para YouTube service"""
        return YouTubeServiceConfig(
            max_retries=2,
            retry_delay=0.1,
            enable_quota_tracking=True,
            daily_quota_limit=1000
        )

    @pytest.fixture
    def mock_youtube_client(self):
        """Mock del cliente de YouTube API"""
        mock_client = Mock()
        mock_search = Mock()
        mock_videos = Mock()
        
        mock_client.search.return_value = mock_search
        mock_client.videos.return_value = mock_videos
        
        # Configurar métodos de búsqueda
        mock_search_list = Mock()
        mock_videos_list = Mock()
        
        mock_search.list.return_value = mock_search_list
        mock_videos.list.return_value = mock_videos_list
        
        # Datos de prueba
        mock_search_list.execute.return_value = {
            'items': [
                {
                    'id': {'videoId': 'test_video_1'},
                    'snippet': {
                        'title': 'Test Song - Test Artist',
                        'description': 'Test description',
                        'channelTitle': 'Test Channel',
                        'publishedAt': '2024-01-01T00:00:00Z'
                    }
                }
            ]
        }
        
        mock_videos_list.execute.return_value = {
            'items': [
                {
                    'id': 'test_video_1',
                    'snippet': {
                        'title': 'Test Song - Test Artist',
                        'description': 'Test description',
                        'channelTitle': 'Test Channel',
                        'publishedAt': '2024-01-01T00:00:00Z'
                    },
                    'contentDetails': {
                        'duration': 'PT3M30S'
                    },
                    'statistics': {
                        'viewCount': '1000',
                        'likeCount': '50'
                    }
                }
            ]
        }
        
        return mock_client

    @pytest.fixture
    def youtube_service(self, mock_settings, youtube_config, mock_youtube_client):
        """Instancia del servicio YouTube con mocks"""
        with patch('common.adapters.media.youtube_service.settings', **mock_settings), \
             patch('common.adapters.media.youtube_service.build', return_value=mock_youtube_client):
            service = YouTubeAPIService(config=youtube_config)
            return service

    def test_init_default_config(self, mock_settings):
        """Test de inicialización con configuración por defecto"""
        with patch('common.adapters.media.youtube_service.settings', **mock_settings), \
             patch('common.adapters.media.youtube_service.build') as mock_build:
            
            service = YouTubeAPIService()
            
            assert service.api_key == 'test_api_key'
            assert service.service_name == 'youtube'
            assert service.api_version == 'v3'
            assert isinstance(service.text_cleaner, TextCleaner)
            assert isinstance(service.metadata_extractor, MusicMetadataExtractor)
            assert isinstance(service.retry_manager, RetryManager)
            assert isinstance(service.circuit_breaker, CircuitBreaker)
            mock_build.assert_called_once()

    def test_init_custom_config(self, mock_settings, youtube_config):
        """Test de inicialización con configuración personalizada"""
        with patch('common.adapters.media.youtube_service.settings', **mock_settings), \
             patch('common.adapters.media.youtube_service.build'):
            
            service = YouTubeAPIService(config=youtube_config)
            
            assert service.config == youtube_config
            assert service.config.max_retries == 2
            assert service.config.retry_delay == 0.1

    def test_build_youtube_client_success(self, mock_settings):
        """Test de construcción exitosa del cliente YouTube"""
        with patch('common.adapters.media.youtube_service.settings', **mock_settings), \
             patch('common.adapters.media.youtube_service.build') as mock_build:
            
            mock_client = Mock()
            mock_build.return_value = mock_client
            
            service = YouTubeAPIService()
            
            mock_build.assert_called_once_with(
                'youtube', 'v3', developerKey='test_api_key'
            )
            assert service.youtube == mock_client

    def test_build_youtube_client_failure(self, mock_settings):
        """Test de fallo en construcción del cliente YouTube"""
        with patch('common.adapters.media.youtube_service.settings', **mock_settings), \
             patch('common.adapters.media.youtube_service.build') as mock_build:
            
            mock_build.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                YouTubeAPIService()

    @pytest.mark.asyncio
    async def test_search_videos_success(self, youtube_service):
        """Test de búsqueda exitosa de videos"""
        query = "test song artist"
        max_results = 5
        
        result = await youtube_service.search_videos(query, max_results)
        
        assert len(result) == 1
        assert result[0].id == 'test_video_1'
        assert result[0].title == 'Test Song - Test Artist'
        assert result[0].channel_title == 'Test Channel'

    @pytest.mark.asyncio
    async def test_search_videos_empty_query(self, youtube_service):
        """Test de búsqueda con query vacío"""
        query = ""
        
        result = await youtube_service.search_videos(query)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_search_videos_http_error(self, youtube_service):
        """Test de manejo de errores HTTP en búsqueda"""
        query = "test query"
        
        # Configurar error HTTP
        youtube_service.youtube.search().list().execute.side_effect = HttpError(
            resp=Mock(status=403), content=b'Quota exceeded'
        )
        
        with pytest.raises(HttpError):
            await youtube_service.search_videos(query)

    @pytest.mark.asyncio
    async def test_get_video_details_success(self, youtube_service):
        """Test de obtención exitosa de detalles del video"""
        video_id = "test_video_1"
        
        result = await youtube_service.get_video_details(video_id)
        
        assert result.id == video_id
        assert result.title == 'Test Song - Test Artist'
        assert result.duration_seconds == 210  # 3:30 en segundos
        assert result.view_count == 1000

    @pytest.mark.asyncio
    async def test_get_video_details_not_found(self, youtube_service):
        """Test de video no encontrado"""
        video_id = "nonexistent_video"
        
        # Configurar respuesta vacía
        youtube_service.youtube.videos().list().execute.return_value = {'items': []}
        
        result = await youtube_service.get_video_details(video_id)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_search_with_options(self, youtube_service):
        """Test de búsqueda con opciones personalizadas"""
        query = "test song"
        options = SearchOptions(
            max_results=10,
            order='relevance',
            video_duration='medium',
            video_category_id='10'  # Music category
        )
        
        result = await youtube_service.search_videos(query, options=options)
        
        assert len(result) >= 0

    def test_parse_duration_standard_format(self, youtube_service):
        """Test de parseo de duración en formato ISO 8601"""
        # PT3M30S = 3 minutos 30 segundos = 210 segundos
        duration = youtube_service._parse_duration("PT3M30S")
        assert duration == 210
        
        # PT2H45M = 2 horas 45 minutos = 9900 segundos
        duration = youtube_service._parse_duration("PT2H45M")
        assert duration == 9900
        
        # PT45S = 45 segundos
        duration = youtube_service._parse_duration("PT45S")
        assert duration == 45

    def test_parse_duration_invalid_format(self, youtube_service):
        """Test de parseo de duración con formato inválido"""
        duration = youtube_service._parse_duration("invalid")
        assert duration == 0
        
        duration = youtube_service._parse_duration("")
        assert duration == 0
        
        duration = youtube_service._parse_duration(None)
        assert duration == 0

    def test_quota_tracking_enabled(self, youtube_service):
        """Test de seguimiento de cuota habilitado"""
        assert youtube_service.enable_quota_tracking is True
        assert youtube_service.quota_used_today == 0

    def test_quota_tracking_update(self, youtube_service):
        """Test de actualización del uso de cuota"""
        initial_quota = youtube_service.quota_used_today
        youtube_service._update_quota_usage(100)
        
        assert youtube_service.quota_used_today == initial_quota + 100

    def test_quota_limit_exceeded(self, youtube_service):
        """Test de límite de cuota excedido"""
        youtube_service.quota_used_today = 1000  # Límite máximo
        
        with pytest.raises(Exception, match="Daily quota limit exceeded"):
            youtube_service._check_quota_limit(100)

    def test_text_cleaning_integration(self, youtube_service):
        """Test de integración con TextCleaner"""
        dirty_text = "Test Song!!! @#$% - Artist Name"
        cleaned = youtube_service.text_cleaner.clean_text(dirty_text)
        
        assert "!!!" not in cleaned
        assert "@#$%" not in cleaned

    @pytest.mark.asyncio
    async def test_circuit_breaker_activation(self, youtube_service):
        """Test de activación del circuit breaker"""
        # Simular múltiples fallos
        youtube_service.youtube.search().list().execute.side_effect = HttpError(
            resp=Mock(status=500), content=b'Internal Server Error'
        )
        
        # Realizar múltiples intentos para activar el circuit breaker
        for _ in range(6):  # Threshold es 5
            try:
                await youtube_service.search_videos("test")
            except HttpError:
                pass
        
        # El circuit breaker debería estar abierto ahora
        assert youtube_service.circuit_breaker.is_open()

    @pytest.mark.asyncio
    async def test_retry_mechanism(self, youtube_service):
        """Test del mecanismo de reintentos"""
        call_count = 0
        
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise HttpError(resp=Mock(status=500), content=b'Server Error')
            return {'items': []}
        
        youtube_service.youtube.search().list().execute.side_effect = side_effect
        
        result = await youtube_service.search_videos("test")
        
        assert call_count == 2  # 1 fallo + 1 éxito
        assert result == []

    def test_video_info_creation(self, youtube_service):
        """Test de creación de objeto YouTubeVideoInfo"""
        video_data = {
            'id': 'test_id',
            'snippet': {
                'title': 'Test Title',
                'description': 'Test Description',
                'channelTitle': 'Test Channel',
                'publishedAt': '2024-01-01T00:00:00Z'
            },
            'contentDetails': {
                'duration': 'PT3M30S'
            },
            'statistics': {
                'viewCount': '1000',
                'likeCount': '50'
            }
        }
        
        video_info = youtube_service._create_video_info(video_data)
        
        assert video_info.id == 'test_id'
        assert video_info.title == 'Test Title'
        assert video_info.description == 'Test Description'
        assert video_info.channel_title == 'Test Channel'
        assert video_info.duration_seconds == 210
        assert video_info.view_count == 1000

    def test_video_info_minimal_data(self, youtube_service):
        """Test de creación de YouTubeVideoInfo con datos mínimos"""
        video_data = {
            'id': 'test_id',
            'snippet': {
                'title': 'Test Title'
            }
        }
        
        video_info = youtube_service._create_video_info(video_data)
        
        assert video_info.id == 'test_id'
        assert video_info.title == 'Test Title'
        assert video_info.description == ''
        assert video_info.duration_seconds == 0
        assert video_info.view_count == 0

    @pytest.mark.asyncio
    async def test_search_with_filters(self, youtube_service):
        """Test de búsqueda con filtros específicos"""
        query = "music video"
        
        # Mock para búsqueda con filtros
        youtube_service.youtube.search().list().execute.return_value = {
            'items': [
                {
                    'id': {'videoId': 'filtered_video'},
                    'snippet': {
                        'title': 'Filtered Music Video',
                        'description': 'Official music video',
                        'channelTitle': 'Official Channel',
                        'publishedAt': '2024-01-01T00:00:00Z'
                    }
                }
            ]
        }
        
        result = await youtube_service.search_videos(
            query,
            max_results=1,
            options=SearchOptions(video_category_id='10')  # Music category
        )
        
        assert len(result) == 1
        assert result[0].id == 'filtered_video'
        assert 'music' in result[0].title.lower()

    def test_logging_integration(self, youtube_service):
        """Test de integración con logging"""
        # Verificar que el servicio tiene logger
        assert hasattr(youtube_service, 'logger')
        assert youtube_service.logger is not None

    @pytest.mark.asyncio
    async def test_metadata_extraction_integration(self, youtube_service):
        """Test de integración con extractor de metadatos"""
        video_id = "test_video_1"
        
        # Mock del extractor de metadatos
        with patch.object(youtube_service.metadata_extractor, 'extract_music_metadata') as mock_extract:
            mock_extract.return_value = Mock(
                extracted_artists=['Test Artist'],
                extracted_albums=['Test Album']
            )
            
            result = await youtube_service.get_video_details(video_id)
            
            mock_extract.assert_called_once()
            assert result is not None

    def test_config_validation(self):
        """Test de validación de configuración"""
        config = YouTubeServiceConfig(
            max_retries=-1,  # Valor inválido
            retry_delay=0,
            daily_quota_limit=0
        )
        
        # El servicio debería manejar configuraciones inválidas
        with patch('common.adapters.media.youtube_service.settings') as mock_settings:
            mock_settings.YOUTUBE_API_KEY = 'test_key'
            mock_settings.YOUTUBE_API_SERVICE_NAME = 'youtube'
            mock_settings.YOUTUBE_API_VERSION = 'v3'
            
            with patch('common.adapters.media.youtube_service.build'):
                service = YouTubeAPIService(config=config)
                
                # Debería usar valores por defecto o válidos
                assert service.config.max_retries >= 0

    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(self, youtube_service):
        """Test de manejo de solicitudes concurrentes"""
        import asyncio
        
        queries = ["song1", "song2", "song3"]
        
        # Ejecutar búsquedas concurrentes
        tasks = [youtube_service.search_videos(query, 1) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verificar que todas las solicitudes se completaron
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)
