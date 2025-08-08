"""
🧪 CONFTEST SIMPLE PARA TESTS
============================
Configuración básica de pytest para tests simples
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Configurar Django antes de cualquier import
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')

# Agregar el directorio src al path para imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent / 'src'
sys.path.insert(0, str(src_dir))

try:
    import django
    django.setup()
except Exception:
    # Si Django no está disponible, continuar sin configurarlo
    pass

# Mock para componentes que requieren configuración especial
@pytest.fixture(autouse=True)
def django_mock():
    """Mock automático para Django si no está disponible"""
    if 'django' not in sys.modules:
        sys.modules['django'] = Mock()
        sys.modules['django.db'] = Mock()
        sys.modules['django.db.models'] = Mock()
        sys.modules['django.core.exceptions'] = Mock()

@pytest.fixture(autouse=True)
def mock_numpy():
    """Mock automático para numpy si no está disponible"""
    if 'numpy' not in sys.modules:
        mock_np = Mock()
        mock_np.array = Mock(return_value=[1, 2, 3])
        mock_np.mean = Mock(return_value=2.0)
        mock_np.std = Mock(return_value=0.5)
        sys.modules['numpy'] = mock_np


@pytest.fixture
def sample_song_data():
    """Datos de prueba para Song"""
    return {
        "id": "song-test-123",
        "title": "Test Song",
        "artist_name": "Test Artist",
        "album_title": "Test Album",
        "genre_name": "Rock",
        "duration_seconds": 180,
        "play_count": 100,
        "is_active": True,
    }


@pytest.fixture
def sample_artist_data():
    """Datos de prueba para Artist"""
    return {
        "id": "artist-test-123",
        "name": "Test Artist",
        "biography": "Una biografía de prueba",
        "country": "Colombia",
        "followers_count": 50000,
        "is_verified": True,
        "is_active": True,
    }


@pytest.fixture
def sample_album_data():
    """Datos de prueba para Album"""
    return {
        "id": "album-test-123",
        "title": "Test Album",
        "artist_name": "Test Artist",
        "release_date": "2024-01-01",
        "total_tracks": 12,
        "is_active": True,
    }


@pytest.fixture
def sample_genre_data():
    """Datos de prueba para Genre"""
    return {
        "id": "genre-test-123",
        "name": "Rock",
        "description": "Rock music genre",
        "is_active": True,
    }


@pytest.fixture
def sample_playlist_data():
    """Datos de prueba para Playlist"""
    return {
        "id": "playlist-test-123",
        "name": "Test Playlist",
        "description": "A test playlist",
        "is_public": True,
        "is_active": True,
    }
