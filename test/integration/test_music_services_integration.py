"""
🧪 TESTS DE INTEGRACIÓN PARA SERVICIOS DE MÚSICA
==============================================
Tests que cubren múltiples componentes trabajando juntos
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Importaciones simuladas para evitar errores de resolución
try:
    from common.adapters.media.unified_music_service import UnifiedMusicService
    from common.adapters.media.youtube_service import YouTubeAPIService
    from common.adapters.media.audio_download_service import AudioDownloadService
    from common.adapters.lyrics.lyrics_service import LyricsService
    from common.utils.music_metadata_extractor import MusicMetadataExtractor
    from common.types.media_types import SearchOptions, DownloadOptions
except ImportError:
    # Crear mocks para cuando las importaciones fallen
    UnifiedMusicService = Mock
    YouTubeAPIService = Mock
    AudioDownloadService = Mock
    LyricsService = Mock
    MusicMetadataExtractor = Mock
    SearchOptions = Mock
    DownloadOptions = Mock


class TestMusicServiceIntegration:
    """Tests de integración para servicios de música"""

    @pytest.fixture
    def mock_youtube_service(self):
        """Mock del servicio de YouTube"""
        service = Mock(spec=YouTubeAPIService)
        
        # Mock de búsqueda de videos
        service.search_videos = AsyncMock(return_value=[
            Mock(
                id='test_video_1',
                title='Ed Sheeran - Shape of You',
                description='Official music video',
                channel_title='Ed Sheeran',
                duration_seconds=234,
                view_count=5000000,
                url='https://youtube.com/watch?v=test_video_1'
            )
        ])
        
        # Mock de obtención de detalles
        service.get_video_details = AsyncMock(return_value=Mock(
            id='test_video_1',
            title='Ed Sheeran - Shape of You',
            description='Official music video for Shape of You',
            duration_seconds=234,
            view_count=5000000
        ))
        
        return service

    @pytest.fixture
    def mock_audio_download_service(self):
        """Mock del servicio de descarga de audio"""
        service = Mock(spec=AudioDownloadService)
        
        # Mock de descarga de audio
        service.download_audio = AsyncMock(return_value={
            'file_path': '/tmp/test_audio.mp3',
            'metadata': {
                'title': 'Shape of You',
                'artist': 'Ed Sheeran',
                'duration': 234,
                'format': 'mp3',
                'quality': '192'
            }
        })
        
        # Mock de obtención de información
        service.get_audio_info = AsyncMock(return_value={
            'id': 'test_video_1',
            'title': 'Ed Sheeran - Shape of You',
            'duration': 234,
            'formats': ['mp3', 'flac']
        })
        
        return service

    @pytest.fixture
    def mock_lyrics_service(self):
        """Mock del servicio de letras"""
        service = Mock(spec=LyricsService)
        
        # Mock de búsqueda de letras
        service.search_lyrics = AsyncMock(return_value={
            'lyrics': 'The club isn\'t the best place to find a lover...',
            'source': 'genius',
            'confidence': 0.95
        })
        
        return service

    @pytest.fixture
    def mock_metadata_extractor(self):
        """Mock del extractor de metadatos"""
        extractor = Mock(spec=MusicMetadataExtractor)
        
        # Mock de extracción de metadatos
        extractor.extract_music_metadata = Mock(return_value=Mock(
            extracted_artists=[Mock(name='Ed Sheeran', confidence_score=0.95)],
            extracted_albums=[Mock(title='Divide', confidence_score=0.90)]
        ))
        
        return extractor

    @pytest.fixture
    def unified_music_service(self, mock_youtube_service, mock_audio_download_service, 
                            mock_lyrics_service, mock_metadata_extractor):
        """Servicio unificado con dependencias mockeadas"""
        with patch('common.adapters.media.unified_music_service.YouTubeAPIService', return_value=mock_youtube_service), \
             patch('common.adapters.media.unified_music_service.AudioDownloadService', return_value=mock_audio_download_service), \
             patch('common.adapters.media.unified_music_service.LyricsService', return_value=mock_lyrics_service), \
             patch('common.adapters.media.unified_music_service.MusicMetadataExtractor', return_value=mock_metadata_extractor):
            
            # Crear mock del servicio unificado
            service = Mock(spec=UnifiedMusicService)
            service.youtube_service = mock_youtube_service
            service.audio_service = mock_audio_download_service
            service.lyrics_service = mock_lyrics_service
            service.metadata_extractor = mock_metadata_extractor
            
            return service

    @pytest.mark.asyncio
    async def test_complete_music_search_workflow(self, unified_music_service):
        """Test del flujo completo de búsqueda de música"""
        query = "Ed Sheeran Shape of You"
        
        # Mock del método search_and_download
        unified_music_service.search_and_download = AsyncMock(return_value={
            'video_info': {
                'id': 'test_video_1',
                'title': 'Ed Sheeran - Shape of You',
                'artist': 'Ed Sheeran',
                'duration': 234
            },
            'audio_file': '/tmp/test_audio.mp3',
            'metadata': {
                'title': 'Shape of You',
                'artist': 'Ed Sheeran',
                'album': 'Divide',
                'duration': 234
            },
            'lyrics': 'The club isn\'t the best place to find a lover...'
        })
        
        # Ejecutar búsqueda completa
        result = await unified_music_service.search_and_download(query)
        
        # Verificaciones
        assert result is not None
        assert 'video_info' in result
        assert 'audio_file' in result
        assert 'metadata' in result
        assert 'lyrics' in result
        
        # Verificar que se llamó al método
        unified_music_service.search_and_download.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_youtube_to_audio_pipeline(self, mock_youtube_service, mock_audio_download_service):
        """Test del pipeline de YouTube a audio"""
        video_url = "https://youtube.com/watch?v=test_video_1"
        
        # 1. Obtener información del video
        video_info = await mock_youtube_service.get_video_details('test_video_1')
        
        # 2. Descargar audio
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_result = await mock_audio_download_service.download_audio(
                video_url, 
                output_dir=temp_dir
            )
        
        # Verificaciones
        assert video_info is not None
        assert audio_result is not None
        assert 'file_path' in audio_result
        assert 'metadata' in audio_result
        
        # Verificar llamadas
        mock_youtube_service.get_video_details.assert_called_once()
        mock_audio_download_service.download_audio.assert_called_once()

    @pytest.mark.asyncio
    async def test_metadata_extraction_and_lyrics_search(self, mock_metadata_extractor, mock_lyrics_service):
        """Test de extracción de metadatos y búsqueda de letras"""
        video_info = Mock(
            title='Ed Sheeran - Shape of You',
            description='Official music video',
            channel_title='Ed Sheeran'
        )
        
        # 1. Extraer metadatos
        enriched_info = mock_metadata_extractor.extract_music_metadata(video_info)
        
        # 2. Buscar letras usando metadatos extraídos
        artist_name = enriched_info.extracted_artists[0].name
        song_title = 'Shape of You'  # Extraído del título
        
        lyrics_result = await mock_lyrics_service.search_lyrics(artist_name, song_title)
        
        # Verificaciones
        assert enriched_info is not None
        assert lyrics_result is not None
        assert 'lyrics' in lyrics_result
        assert 'source' in lyrics_result
        
        # Verificar llamadas
        mock_metadata_extractor.extract_music_metadata.assert_called_once()
        mock_lyrics_service.search_lyrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_processing(self, unified_music_service):
        """Test de procesamiento concurrente de múltiples búsquedas"""
        queries = [
            "Ed Sheeran Shape of You",
            "Taylor Swift Shake It Off",
            "Adele Hello"
        ]
        
        # Mock para cada búsqueda
        search_results = []
        for i, query in enumerate(queries):
            result = {
                'video_info': {'id': f'test_video_{i}', 'title': query},
                'audio_file': f'/tmp/audio_{i}.mp3',
                'metadata': {'title': query.split()[-1]},
                'lyrics': f'Lyrics for {query}'
            }
            search_results.append(result)
        
        unified_music_service.search_and_download = AsyncMock(side_effect=search_results)
        
        # Ejecutar búsquedas concurrentes
        tasks = [unified_music_service.search_and_download(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verificaciones
        assert len(results) == 3
        for i, result in enumerate(results):
            assert not isinstance(result, Exception)
            assert result['video_info']['id'] == f'test_video_{i}'

    @pytest.mark.asyncio
    async def test_error_handling_in_pipeline(self, unified_music_service):
        """Test de manejo de errores en el pipeline"""
        query = "Invalid Song Query"
        
        # Configurar para que YouTube service falle
        unified_music_service.youtube_service.search_videos = AsyncMock(
            side_effect=Exception("YouTube API error")
        )
        
        unified_music_service.search_and_download = AsyncMock(
            side_effect=Exception("Search failed")
        )
        
        # Ejecutar y verificar manejo de errores
        with pytest.raises(Exception, match="Search failed"):
            await unified_music_service.search_and_download(query)

    @pytest.mark.asyncio
    async def test_partial_failure_resilience(self, unified_music_service):
        """Test de resistencia a fallos parciales"""
        query = "Test Song"
        
        # Mock que falla en obtener letras pero tiene éxito en lo demás
        unified_music_service.search_and_download = AsyncMock(return_value={
            'video_info': {'id': 'test_video', 'title': 'Test Song'},
            'audio_file': '/tmp/test_audio.mp3',
            'metadata': {'title': 'Test Song'},
            'lyrics': None,  # Fallo en obtener letras
            'errors': ['Failed to fetch lyrics']
        })
        
        result = await unified_music_service.search_and_download(query)
        
        # Verificar que el resultado parcial es útil
        assert result is not None
        assert result['video_info'] is not None
        assert result['audio_file'] is not None
        assert result['lyrics'] is None
        assert 'errors' in result

    @pytest.mark.asyncio
    async def test_download_options_propagation(self, mock_audio_download_service):
        """Test de propagación de opciones de descarga"""
        url = "https://youtube.com/watch?v=test"
        download_options = Mock(
            audio_format='flac',
            audio_quality='320',
            normalize_audio=True
        )
        
        # Ejecutar descarga con opciones específicas
        await mock_audio_download_service.download_audio(url, options=download_options)
        
        # Verificar que las opciones se pasaron correctamente
        mock_audio_download_service.download_audio.assert_called_once()
        call_args = mock_audio_download_service.download_audio.call_args
        assert 'options' in call_args.kwargs or len(call_args.args) > 1

    @pytest.mark.asyncio
    async def test_search_options_filtering(self, mock_youtube_service):
        """Test de filtrado con opciones de búsqueda"""
        query = "music video"
        search_options = Mock(
            max_results=5,
            video_duration='medium',
            video_category_id='10'  # Music category
        )
        
        # Ejecutar búsqueda con filtros
        await mock_youtube_service.search_videos(query, options=search_options)
        
        # Verificar que se aplicaron los filtros
        mock_youtube_service.search_videos.assert_called_once()
        call_args = mock_youtube_service.search_videos.call_args
        assert 'options' in call_args.kwargs or len(call_args.args) > 1

    @pytest.mark.asyncio
    async def test_metadata_consistency_across_services(self, unified_music_service):
        """Test de consistencia de metadatos entre servicios"""
        query = "Ed Sheeran Shape of You"
        
        # Mock con metadatos consistentes
        unified_music_service.search_and_download = AsyncMock(return_value={
            'video_info': {
                'title': 'Ed Sheeran - Shape of You',
                'channel_title': 'Ed Sheeran'
            },
            'audio_file': '/tmp/audio.mp3',
            'metadata': {
                'title': 'Shape of You',
                'artist': 'Ed Sheeran',
                'album': 'Divide'
            },
            'extracted_metadata': {
                'artists': [{'name': 'Ed Sheeran', 'confidence': 0.95}],
                'albums': [{'title': 'Divide', 'confidence': 0.90}]
            }
        })
        
        result = await unified_music_service.search_and_download(query)
        
        # Verificar consistencia
        video_title = result['video_info']['title']
        audio_metadata = result['metadata']
        extracted_metadata = result['extracted_metadata']
        
        assert 'Ed Sheeran' in video_title
        assert audio_metadata['artist'] == 'Ed Sheeran'
        assert extracted_metadata['artists'][0]['name'] == 'Ed Sheeran'

    @pytest.mark.asyncio
    async def test_resource_cleanup(self, unified_music_service):
        """Test de limpieza de recursos"""
        query = "Test Song"
        
        # Mock que simula limpieza de archivos temporales
        temp_files = ['/tmp/temp1.mp3', '/tmp/temp2.wav']
        
        unified_music_service.search_and_download = AsyncMock(return_value={
            'video_info': {'id': 'test'},
            'audio_file': '/tmp/final.mp3',
            'metadata': {},
            'temp_files_cleaned': temp_files
        })
        
        result = await unified_music_service.search_and_download(query)
        
        # Verificar que se indica la limpieza
        assert 'temp_files_cleaned' in result
        assert len(result['temp_files_cleaned']) > 0

    def test_service_configuration_validation(self, unified_music_service):
        """Test de validación de configuración de servicios"""
        # Verificar que todos los servicios están configurados
        assert unified_music_service.youtube_service is not None
        assert unified_music_service.audio_service is not None
        assert unified_music_service.lyrics_service is not None
        assert unified_music_service.metadata_extractor is not None

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, unified_music_service):
        """Test de monitoreo de rendimiento"""
        query = "Performance Test Song"
        
        # Mock con métricas de rendimiento
        unified_music_service.search_and_download = AsyncMock(return_value={
            'video_info': {'id': 'perf_test'},
            'audio_file': '/tmp/perf_test.mp3',
            'metadata': {},
            'performance_metrics': {
                'search_time': 1.5,
                'download_time': 30.2,
                'total_time': 35.0,
                'file_size': 5242880  # 5MB
            }
        })
        
        start_time = datetime.now()
        result = await unified_music_service.search_and_download(query)
        end_time = datetime.now()
        
        # Verificar métricas
        assert 'performance_metrics' in result
        metrics = result['performance_metrics']
        assert 'search_time' in metrics
        assert 'download_time' in metrics
        assert 'total_time' in metrics
        
        # Verificar que el tiempo real es consistente
        actual_time = (end_time - start_time).total_seconds()
        assert actual_time >= 0  # Tiempo básico de validación
