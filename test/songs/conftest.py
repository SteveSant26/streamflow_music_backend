"""
Configuración base para tests de songs
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Configurar paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

# Configurar Django para tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django

django.setup()


class SongsTestConfig:
    """Configuración específica para tests de songs"""

    # Base de datos de testing en memoria
    TEST_DATABASE = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

    # Datos de prueba para canciones
    SAMPLE_SONG_DATA = {
        "id": "song-123",
        "title": "Test Song",
        "album_id": "album-456",
        "artist_id": "artist-789",
        "genre_id": "genre-101",
        "duration_seconds": 180,
        "album_title": "Test Album",
        "artist_name": "Test Artist",
        "genre_name": "Rock",
        "track_number": 1,
        "file_url": "https://example.com/song.mp3",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "lyrics": "Test lyrics",
        "tags": ["rock", "classic"],
        "play_count": 100,
        "favorite_count": 10,
        "download_count": 5,
        "spotify_id": "spotify-123",
        "apple_music_id": "apple-123",
        "deezer_id": "deezer-123",
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    # Múltiples canciones para tests de listas
    SAMPLE_SONGS_LIST = [
        {
            "id": f"song-{i}",
            "title": f"Test Song {i}",
            "album_id": f"album-{i}",
            "artist_id": f"artist-{i}",
            "genre_id": f"genre-{i}",
            "duration_seconds": 180 + i * 10,
            "album_title": f"Test Album {i}",
            "artist_name": f"Test Artist {i}",
            "genre_name": "Rock",
            "track_number": i,
            "play_count": 100 - i * 5,
            "favorite_count": 10 - i,
            "download_count": 5,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        for i in range(1, 6)
    ]

    # Datos inválidos para tests de validación
    INVALID_SONG_DATA = {
        "id": "",  # ID vacío
        "title": "",  # Título vacío
        "duration_seconds": -1,  # Duración inválida
        "play_count": -5,  # Count negativo
    }


def get_test_settings() -> Dict[str, Any]:
    """
    Obtiene configuración de Django optimizada para tests
    """
    return {
        "DATABASES": {"default": SongsTestConfig.TEST_DATABASE},
        "USE_TZ": True,
        "SECRET_KEY": "test-secret-key",
        "DEBUG": True,
        "TESTING": True,
    }
