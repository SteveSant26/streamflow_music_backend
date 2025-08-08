"""
🧪 TESTS UNITARIOS PARA AUDIO DOWNLOAD SERVICE
============================================
Tests completos para el servicio de descarga de audio
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from common.adapters.media.audio_download_service import AudioDownloadService
from common.types.media_types import AudioServiceConfig, DownloadOptions
from common.utils.validators import URLValidator, MediaDataValidator
from common.utils.retry_manager import RetryManager
from common.utils.youtube_error_handler import YouTubeErrorHandler


class TestAudioDownloadService:
    """Tests unitarios para AudioDownloadService"""

    @pytest.fixture
    def audio_config(self):
        """Configuración de prueba para el servicio de audio"""
        return AudioServiceConfig(
            max_retries=2,
            retry_delay=0.1,
            max_file_size_mb=50,
            audio_quality='192'
        )

    @pytest.fixture
    def download_options(self):
        """Opciones de descarga de prueba"""
        return DownloadOptions(
            audio_format='mp3',
            audio_quality='192',
            extract_metadata=True,
            normalize_audio=False
        )

    @pytest.fixture
    def mock_yt_dlp(self):
        """Mock de yt-dlp"""
        with patch('common.adapters.media.audio_download_service.yt_dlp') as mock:
            yield mock

    @pytest.fixture
    def audio_service(self, audio_config, download_options, mock_yt_dlp):
        """Instancia del servicio de descarga de audio"""
        with patch('src.config.music_service_config.get_optimized_ydl_options') as mock_config:
            mock_config.return_value = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3'
            }
            return AudioDownloadService(config=audio_config, default_options=download_options)

    def test_init_default_config(self, mock_yt_dlp):
        """Test de inicialización con configuración por defecto"""
        with patch('src.config.music_service_config.get_optimized_ydl_options') as mock_config:
            mock_config.return_value = {}
            
            service = AudioDownloadService()
            
            assert service.config is not None
            assert service.default_options is not None
            assert isinstance(service.url_validator, URLValidator)
            assert isinstance(service.media_validator, MediaDataValidator)
            assert isinstance(service.retry_manager, RetryManager)
            assert isinstance(service.error_handler, YouTubeErrorHandler)

    def test_init_custom_config(self, audio_config, download_options, mock_yt_dlp):
        """Test de inicialización con configuración personalizada"""
        with patch('src.config.music_service_config.get_optimized_ydl_options') as mock_config:
            mock_config.return_value = {}
            
            service = AudioDownloadService(config=audio_config, default_options=download_options)
            
            assert service.config == audio_config
            assert service.default_options == download_options
            assert service.config.max_retries == 2
            assert service.config.retry_delay == 0.1

    def test_build_base_ydl_options(self, audio_service):
        """Test de construcción de opciones base para yt-dlp"""
        options = audio_service._base_ydl_opts
        
        assert 'outtmpl' in options
        assert isinstance(options, dict)

    @pytest.mark.asyncio
    async def test_download_audio_success(self, audio_service, mock_yt_dlp):
        """Test de descarga exitosa de audio"""
        url = "https://youtube.com/watch?v=test123"
        
        # Mock del contexto YoutubeDL
        mock_ydl = Mock()
        mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {
            'id': 'test123',
            'title': 'Test Song',
            'duration': 180,
            'uploader': 'Test Channel'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await audio_service.download_audio(url, output_dir=temp_dir)
            
            assert result is not None
            assert 'file_path' in result
            assert 'metadata' in result

    @pytest.mark.asyncio
    async def test_download_audio_invalid_url(self, audio_service):
        """Test de descarga con URL inválida"""
        invalid_url = "not_a_valid_url"
        
        with pytest.raises(ValueError, match="Invalid URL"):
            await audio_service.download_audio(invalid_url)

    @pytest.mark.asyncio
    async def test_download_audio_with_custom_options(self, audio_service, mock_yt_dlp):
        """Test de descarga con opciones personalizadas"""
        url = "https://youtube.com/watch?v=test123"
        custom_options = DownloadOptions(
            audio_format='flac',
            audio_quality='320',
            extract_metadata=True
        )
        
        mock_ydl = Mock()
        mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {
            'id': 'test123',
            'title': 'Test Song'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await audio_service.download_audio(
                url, 
                output_dir=temp_dir,
                options=custom_options
            )
            
            assert result is not None

    @pytest.mark.asyncio
    async def test_download_audio_file_too_large(self, audio_service, mock_yt_dlp):
        """Test de descarga con archivo demasiado grande"""
        url = "https://youtube.com/watch?v=test123"
        
        mock_ydl = Mock()
        mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {
            'id': 'test123',
            'title': 'Test Song',
            'filesize': 100 * 1024 * 1024  # 100MB (excede el límite de 50MB)
        }
        
        with pytest.raises(ValueError, match="File too large"):
            await audio_service.download_audio(url)

    @pytest.mark.asyncio
    async def test_download_audio_retry_mechanism(self, audio_service, mock_yt_dlp):
        """Test del mecanismo de reintentos"""
        url = "https://youtube.com/watch?v=test123"
        
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary error")
            return {'id': 'test123', 'title': 'Test Song'}
        
        mock_ydl = Mock()
        mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = side_effect
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await audio_service.download_audio(url, output_dir=temp_dir)
            
            assert call_count == 2  # 1 fallo + 1 éxito
            assert result is not None

    @pytest.mark.asyncio
    async def test_download_audio_max_retries_exceeded(self, audio_service, mock_yt_dlp):
        """Test de exceso de reintentos máximos"""
        url = "https://youtube.com/watch?v=test123"
        
        mock_ydl = Mock()
        mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = Exception("Persistent error")
        
        with pytest.raises(Exception):
            await audio_service.download_audio(url)

    @pytest.mark.asyncio
    async def test_get_audio_info_success(self, audio_service, mock_yt_dlp):
        """Test de obtención exitosa de información de audio"""
        url = "https://youtube.com/watch?v=test123"
        
        mock_ydl = Mock()
        mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {
            'id': 'test123',
            'title': 'Test Song',
            'duration': 180,
            'uploader': 'Test Channel',
            'view_count': 1000000
        }
        
        result = await audio_service.get_audio_info(url)
        
        assert result['id'] == 'test123'
        assert result['title'] == 'Test Song'
        assert result['duration'] == 180

    @pytest.mark.asyncio
    async def test_get_audio_info_invalid_url(self, audio_service):
        """Test de obtención de info con URL inválida"""
        invalid_url = "invalid_url"
        
        with pytest.raises(ValueError):
            await audio_service.get_audio_info(invalid_url)

    def test_merge_download_options(self, audio_service):
        """Test de fusión de opciones de descarga"""
        custom_options = DownloadOptions(
            audio_format='flac',
            audio_quality='320'
        )
        
        merged = audio_service._merge_download_options(custom_options)
        
        assert merged.audio_format == 'flac'
        assert merged.audio_quality == '320'

    def test_build_ydl_options_mp3(self, audio_service):
        """Test de construcción de opciones para MP3"""
        options = DownloadOptions(
            audio_format='mp3',
            audio_quality='192'
        )
        
        ydl_opts = audio_service._build_ydl_options(options, '/tmp')
        
        assert 'postprocessors' in ydl_opts
        assert any(pp.get('preferredcodec') == 'mp3' for pp in ydl_opts['postprocessors'])

    def test_build_ydl_options_flac(self, audio_service):
        """Test de construcción de opciones para FLAC"""
        options = DownloadOptions(
            audio_format='flac',
            audio_quality='320'
        )
        
        ydl_opts = audio_service._build_ydl_options(options, '/tmp')
        
        assert 'postprocessors' in ydl_opts
        assert any(pp.get('preferredcodec') == 'flac' for pp in ydl_opts['postprocessors'])

    def test_validate_file_size_valid(self, audio_service):
        """Test de validación de tamaño de archivo válido"""
        file_size = 30 * 1024 * 1024  # 30MB
        
        # No debería lanzar excepción
        audio_service._validate_file_size(file_size)

    def test_validate_file_size_too_large(self, audio_service):
        """Test de validación de archivo demasiado grande"""
        file_size = 100 * 1024 * 1024  # 100MB
        
        with pytest.raises(ValueError, match="File too large"):
            audio_service._validate_file_size(file_size)

    def test_extract_metadata_from_info(self, audio_service):
        """Test de extracción de metadatos"""
        info = {
            'id': 'test123',
            'title': 'Test Song - Artist Name',
            'duration': 180,
            'uploader': 'Artist Channel',
            'view_count': 1000000,
            'upload_date': '20240101'
        }
        
        metadata = audio_service._extract_metadata_from_info(info)
        
        assert metadata['id'] == 'test123'
        assert metadata['title'] == 'Test Song - Artist Name'
        assert metadata['duration'] == 180
        assert metadata['channel'] == 'Artist Channel'

    def test_extract_metadata_minimal_info(self, audio_service):
        """Test de extracción con información mínima"""
        info = {
            'id': 'test123',
            'title': 'Test Song'
        }
        
        metadata = audio_service._extract_metadata_from_info(info)
        
        assert metadata['id'] == 'test123'
        assert metadata['title'] == 'Test Song'
        assert 'duration' in metadata
        assert 'channel' in metadata

    def test_cleanup_temp_files(self, audio_service):
        """Test de limpieza de archivos temporales"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo temporal
            temp_file = os.path.join(temp_dir, 'test_file.tmp')
            with open(temp_file, 'w') as f:
                f.write('test')
            
            assert os.path.exists(temp_file)
            
            audio_service._cleanup_temp_files([temp_file])
            
            assert not os.path.exists(temp_file)

    def test_generate_output_filename(self, audio_service):
        """Test de generación de nombre de archivo"""
        info = {
            'id': 'test123',
            'title': 'Test Song - Artist Name'
        }
        options = DownloadOptions(audio_format='mp3')
        
        filename = audio_service._generate_output_filename(info, options)
        
        assert filename.endswith('.mp3')
        assert 'test123' in filename

    def test_normalize_audio_enabled(self, audio_service):
        """Test de normalización de audio habilitada"""
        options = DownloadOptions(normalize_audio=True)
        file_path = '/tmp/test.mp3'
        
        # Mock del normalizador de audio
        with patch.object(audio_service, '_normalize_audio_file') as mock_normalize:
            audio_service._apply_post_processing(file_path, options)
            mock_normalize.assert_called_once_with(file_path)

    def test_normalize_audio_disabled(self, audio_service):
        """Test de normalización de audio deshabilitada"""
        options = DownloadOptions(normalize_audio=False)
        file_path = '/tmp/test.mp3'
        
        # Mock del normalizador de audio
        with patch.object(audio_service, '_normalize_audio_file') as mock_normalize:
            audio_service._apply_post_processing(file_path, options)
            mock_normalize.assert_not_called()

    def test_error_handler_integration(self, audio_service):
        """Test de integración con manejador de errores"""
        assert audio_service.error_handler is not None
        assert isinstance(audio_service.error_handler, YouTubeErrorHandler)

    def test_url_validator_integration(self, audio_service):
        """Test de integración con validador de URL"""
        assert audio_service.url_validator is not None
        assert isinstance(audio_service.url_validator, URLValidator)

    def test_media_validator_integration(self, audio_service):
        """Test de integración con validador de medios"""
        assert audio_service.media_validator is not None
        assert isinstance(audio_service.media_validator, MediaDataValidator)

    @pytest.mark.asyncio
    async def test_concurrent_downloads(self, audio_service, mock_yt_dlp):
        """Test de descargas concurrentes"""
        urls = [
            "https://youtube.com/watch?v=test1",
            "https://youtube.com/watch?v=test2",
            "https://youtube.com/watch?v=test3"
        ]
        
        mock_ydl = Mock()
        mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {
            'id': 'test',
            'title': 'Test Song'
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Ejecutar descargas concurrentes
            tasks = [
                audio_service.download_audio(url, output_dir=temp_dir) 
                for url in urls
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verificar que todas las descargas se completaron
            assert len(results) == 3
            for result in results:
                assert not isinstance(result, Exception)

    def test_logging_integration(self, audio_service):
        """Test de integración con logging"""
        assert hasattr(audio_service, 'logger')
        assert audio_service.logger is not None

    @pytest.mark.asyncio
    async def test_download_audio_network_error(self, audio_service, mock_yt_dlp):
        """Test de manejo de errores de red"""
        url = "https://youtube.com/watch?v=test123"
        
        mock_ydl = Mock()
        mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = ConnectionError("Network error")
        
        with pytest.raises(ConnectionError):
            await audio_service.download_audio(url)

    def test_config_validation(self, mock_yt_dlp):
        """Test de validación de configuración"""
        invalid_config = AudioServiceConfig(
            max_retries=-1,  # Valor inválido
            retry_delay=-1,  # Valor inválido
            max_file_size_mb=0  # Valor inválido
        )
        
        with patch('src.config.music_service_config.get_optimized_ydl_options') as mock_config:
            mock_config.return_value = {}
            
            # El servicio debería manejar configuraciones inválidas
            service = AudioDownloadService(config=invalid_config)
            
            # Verificar que se aplicaron valores válidos por defecto
            assert service.config.max_retries >= 0
            assert service.config.retry_delay >= 0
            assert service.config.max_file_size_mb > 0
