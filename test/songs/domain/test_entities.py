"""
Tests para entidades del dominio de Songs
"""
<<<<<<< HEAD

=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
# Configurar path antes de importar
import sys
import unittest
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from apps.songs.domain.entities import SongEntity


class TestSongEntity(unittest.TestCase):
    """Tests para la entidad SongEntity"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.valid_song_data = {
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
            "lyrics": "Test lyrics for the song",
            "tags": ["rock", "classic", "guitar"],
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
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    def test_create_song_entity_with_valid_data(self):
        """Test crear entidad con datos válidos"""
        song = SongEntity(**self.valid_song_data)

        self.assertEqual(song.id, "song-123")
        self.assertEqual(song.title, "Test Song")
        self.assertEqual(song.duration_seconds, 180)
        self.assertEqual(song.artist_name, "Test Artist")
        self.assertEqual(song.album_title, "Test Album")
        self.assertEqual(song.genre_name, "Rock")
        self.assertEqual(song.play_count, 100)
        self.assertEqual(song.favorite_count, 10)
        self.assertFalse(song.is_explicit)
        self.assertTrue(song.is_active)
        self.assertFalse(song.is_premium)

    def test_create_song_entity_with_minimal_data(self):
        """Test crear entidad con datos mínimos requeridos"""
        minimal_data = {"id": "song-minimal", "title": "Minimal Song"}

        song = SongEntity(**minimal_data)

        self.assertEqual(song.id, "song-minimal")
        self.assertEqual(song.title, "Minimal Song")
        self.assertEqual(song.duration_seconds, 0)
        self.assertEqual(song.play_count, 0)
        self.assertEqual(song.favorite_count, 0)
        self.assertEqual(song.download_count, 0)
        self.assertIsNone(song.album_id)
        self.assertIsNone(song.artist_id)
        self.assertIsNone(song.genre_id)
        self.assertTrue(song.is_active)
        self.assertFalse(song.is_explicit)
        self.assertFalse(song.is_premium)
        self.assertEqual(song.source_type, "youtube")
        self.assertEqual(song.audio_quality, "standard")

    def test_song_entity_tags_initialization(self):
        """Test que los tags se inicializan correctamente"""
        # Con tags proporcionados
        song_with_tags = SongEntity(
            id="song-with-tags", title="Song with Tags", tags=["rock", "classic"]
        )
        self.assertEqual(song_with_tags.tags, ["rock", "classic"])

        # Sin tags proporcionados (debería inicializar lista vacía)
        song_without_tags = SongEntity(
            id="song-without-tags", title="Song without Tags"
        )
        self.assertEqual(song_without_tags.tags, [])

    def test_song_entity_durations(self):
        """Test manejo de duraciones de canciones"""
        test_cases = [
            (0, 0),  # Sin duración
            (30, 30),  # 30 segundos
            (180, 180),  # 3 minutos
            (3600, 3600),  # 1 hora
        ]

        for duration, expected in test_cases:
            with self.subTest(duration=duration):
                song = SongEntity(
                    id=f"song-{duration}",
                    title=f"Song {duration}s",
                    duration_seconds=duration,
                )
                self.assertEqual(song.duration_seconds, expected)

    def test_song_entity_play_counts(self):
        """Test contadores de reproducción, favoritos y descargas"""
        song = SongEntity(
            id="song-stats",
            title="Song with Stats",
            play_count=1000,
            favorite_count=50,
            download_count=25,
        )

        self.assertEqual(song.play_count, 1000)
        self.assertEqual(song.favorite_count, 50)
        self.assertEqual(song.download_count, 25)

    def test_song_entity_urls(self):
        """Test URLs de archivo y thumbnail"""
        song = SongEntity(
            id="song-urls",
            title="Song with URLs",
            file_url="https://storage.example.com/songs/song.mp3",
            thumbnail_url="https://storage.example.com/thumbs/thumb.jpg",
        )

        self.assertEqual(song.file_url, "https://storage.example.com/songs/song.mp3")
        self.assertEqual(
            song.thumbnail_url, "https://storage.example.com/thumbs/thumb.jpg"
        )

    def test_song_entity_source_metadata(self):
        """Test metadatos de origen de la canción"""
        song = SongEntity(
            id="song-source",
            title="Song with Source",
            source_type="youtube",
            source_id="youtube-456",
            source_url="https://youtube.com/watch?v=456",
        )

        self.assertEqual(song.source_type, "youtube")
        self.assertEqual(song.source_id, "youtube-456")
        self.assertEqual(song.source_url, "https://youtube.com/watch?v=456")

    def test_song_entity_flags(self):
        """Test flags booleanos de la canción"""
        song = SongEntity(
            id="song-flags",
            title="Song with Flags",
            is_explicit=True,
            is_active=False,
            is_premium=True,
        )

        self.assertTrue(song.is_explicit)
        self.assertFalse(song.is_active)
        self.assertTrue(song.is_premium)

    def test_song_entity_audio_quality(self):
        """Test calidad de audio"""
        quality_options = ["standard", "high", "lossless"]

        for quality in quality_options:
            with self.subTest(quality=quality):
                song = SongEntity(
                    id=f"song-{quality}",
                    title=f"Song {quality} Quality",
                    audio_quality=quality,
                )
                self.assertEqual(song.audio_quality, quality)

    def test_song_entity_timestamps(self):
        """Test manejo de timestamps"""
        now = datetime.now()
        release_date = datetime(2023, 1, 15)

        song = SongEntity(
            id="song-timestamps",
            title="Song with Timestamps",
            created_at=now,
            updated_at=now,
            last_played_at=now,
            release_date=release_date,
        )

        self.assertEqual(song.created_at, now)
        self.assertEqual(song.updated_at, now)
        self.assertEqual(song.last_played_at, now)
        self.assertEqual(song.release_date, release_date)

    def test_song_entity_track_number(self):
        """Test número de track en álbum"""
        song = SongEntity(id="song-track", title="Track 5", track_number=5)

        self.assertEqual(song.track_number, 5)

    def test_song_entity_lyrics(self):
        """Test letras de la canción"""
        lyrics = """Verse 1:
This is a test song
With multiple lines
Of lyrics content

Chorus:
Test, test, test
This is just a test"""

        song = SongEntity(id="song-lyrics", title="Song with Lyrics", lyrics=lyrics)

        self.assertEqual(song.lyrics, lyrics)
        self.assertIn("Verse 1:", song.lyrics)
        self.assertIn("Chorus:", song.lyrics)


if __name__ == "__main__":
    unittest.main()
