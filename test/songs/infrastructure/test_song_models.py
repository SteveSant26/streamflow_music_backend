"""
Tests para modelos de la infraestructura de Songs
"""
# Configurar path antes de importar
import sys
import unittest
from pathlib import Path

from django.test import TestCase

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from src.apps.songs.infrastructure.models.song_model import Song


class TestSongModel(TestCase):
    """Tests para el modelo Song"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.valid_song_data = {
            "title": "Test Song",
            "album_title": "Test Album",
            "artist_name": "Test Artist",
            "genre_name": "Rock",
            "duration_seconds": 180,
            "track_number": 1,
            "file_url": "https://example.com/song.mp3",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "lyrics": "Test lyrics content",
            "tags": ["rock", "classic"],
            "play_count": 100,
            "favorite_count": 10,
            "download_count": 5,
            "source_type": "youtube",
            "source_id": "youtube-123",
            "source_url": "https://youtube.com/watch?v=123",
            "is_explicit": False,
            "is_active": True,
            "is_premium": False,
            "audio_quality": "standard",
        }

    def test_create_song_with_valid_data(self):
        """Test crear canción con datos válidos"""
        song = Song.objects.create(**self.valid_song_data)

        self.assertIsNotNone(song.id)
        self.assertEqual(song.title, "Test Song")
        self.assertEqual(song.artist_name, "Test Artist")
        self.assertEqual(song.album_title, "Test Album")
        self.assertEqual(song.genre_name, "Rock")
        self.assertEqual(song.duration_seconds, 180)
        self.assertEqual(song.play_count, 100)
        self.assertTrue(song.is_active)
        self.assertFalse(song.is_explicit)

    def test_create_song_with_minimal_data(self):
        """Test crear canción con datos mínimos"""
        song = Song.objects.create(title="Minimal Song")

        self.assertIsNotNone(song.id)
        self.assertEqual(song.title, "Minimal Song")
        self.assertEqual(song.duration_seconds, 0)
        self.assertEqual(song.play_count, 0)
        self.assertEqual(song.favorite_count, 0)
        self.assertEqual(song.download_count, 0)
        self.assertTrue(song.is_active)
        self.assertFalse(song.is_explicit)
        self.assertFalse(song.is_premium)
        self.assertEqual(song.source_type, "youtube")
        self.assertEqual(song.audio_quality, "standard")


if __name__ == "__main__":
    unittest.main()
