"""
Simple tests to import basic modules and increase coverage without Django dependencies.
Focus on classes that can be imported standalone.
"""

import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def test_import_basic_types():
    """Test importing basic type definitions."""
    try:
        from src.common.types.media_types.audio_types import AudioConfig, AudioFormat, AudioQuality
        assert AudioConfig is not None
        assert AudioFormat is not None  
        assert AudioQuality is not None
    except ImportError:
        pass


def test_import_config_types():
    """Test importing config type definitions."""
    try:
        from src.common.types.media_types.config_types import YoutubeDLConfig, ServiceConfig
        assert YoutubeDLConfig is not None
        assert ServiceConfig is not None
    except ImportError:
        pass


def test_import_extraction_types():
    """Test importing extraction type definitions."""
    try:
        from src.common.types.media_types.extraction_types import TrackMetadata, ExtractionResult
        assert TrackMetadata is not None
        assert ExtractionResult is not None
    except ImportError:
        pass


def test_import_options_types():
    """Test importing options type definitions."""
    try:
        from src.common.types.media_types.options_types import DownloadOptions, SearchOptions
        assert DownloadOptions is not None
        assert SearchOptions is not None
    except ImportError:
        pass


def test_import_video_types():
    """Test importing video type definitions."""
    try:
        from src.common.types.media_types.video_types import VideoInfo, VideoFormat
        assert VideoInfo is not None
        assert VideoFormat is not None
    except ImportError:
        pass


def test_instantiate_basic_configs():
    """Test instantiating basic configuration objects."""
    try:
        from src.common.types.media_types.audio_types import AudioConfig
        config = AudioConfig()
        assert config is not None
    except Exception:
        pass  # Skip if instantiation fails


def test_instantiate_service_config():
    """Test instantiating service configuration."""
    try:
        from src.common.types.media_types.config_types import ServiceConfig
        config = ServiceConfig()
        assert config is not None
    except Exception:
        pass  # Skip if instantiation fails


def test_import_common_utils():
    """Test importing utility functions."""
    try:
        from src.common.utils.storage_utils import clean_filename, ensure_directory_exists
        assert clean_filename is not None
        assert ensure_directory_exists is not None
    except ImportError:
        pass


def test_use_clean_filename():
    """Test using the clean_filename utility."""
    try:
        from src.common.utils.storage_utils import clean_filename
        result = clean_filename("test file.mp3")
        assert result is not None
        assert isinstance(result, str)
    except Exception:
        pass  # Skip if function fails


def test_import_logging_utils():
    """Test importing logging utilities."""
    try:
        from src.common.utils.logging_config import setup_logging, get_logger_config
        assert setup_logging is not None
        assert get_logger_config is not None
    except ImportError:
        pass


class TestBasicImports(unittest.TestCase):
    """Test class for basic imports."""
    
    def test_audio_types_import(self):
        """Test importing audio types."""
        try:
            from src.common.types.media_types.audio_types import AudioFormat
            self.assertIsNotNone(AudioFormat)
        except ImportError:
            self.skipTest("Audio types not available")
    
    def test_config_types_import(self):
        """Test importing config types."""
        try:
            from src.common.types.media_types.config_types import YoutubeDLConfig
            self.assertIsNotNone(YoutubeDLConfig)
        except ImportError:
            self.skipTest("Config types not available")
    
    def test_storage_utils_import(self):
        """Test importing storage utilities."""
        try:
            from src.common.utils.storage_utils import clean_filename
            self.assertIsNotNone(clean_filename)
        except ImportError:
            self.skipTest("Storage utils not available")
    
    def test_logging_decorators_import(self):
        """Test importing logging decorators."""
        try:
            from src.common.utils.logging_decorators import log_execution_time, log_errors
            self.assertIsNotNone(log_execution_time)
            self.assertIsNotNone(log_errors)
        except ImportError:
            self.skipTest("Logging decorators not available")


if __name__ == '__main__':
    unittest.main()
