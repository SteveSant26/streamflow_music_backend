"""
🧪 CONFTEST SIMPLE PARA TESTS
============================
Configuración básica de pytest para tests simples
"""
import pytest
import sys
from pathlib import Path

# Agregar el directorio actual al path para imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


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
