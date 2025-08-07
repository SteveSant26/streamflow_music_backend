"""
Tests para modelos de infraestructura de Songs
"""
<<<<<<< HEAD

=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
# Configurar path antes de importar
import sys
import unittest
import uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from apps.songs.infrastructure.models.song_model import Song


class TestSongModel(TestCase):
    """Tests para el modelo Song de Django"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.valid_song_data = {
            "title": "Test Song",
            "album_id": uuid.uuid4(),
            "artist_id": uuid.uuid4(),
            "genre_id": uuid.uuid4(),
            "album_title": "Test Album",
            "artist_name": "Test Artist",
            "genre_name": "Rock",
            "duration_seconds": 180,
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
        }

    def test_create_song_with_valid_data(self):
        """Test crear canción con datos válidos"""
        song = Song.objects.create(**self.valid_song_data)

        # Verificar que se creó correctamente
        self.assertIsInstance(song.id, uuid.UUID)
        self.assertEqual(song.title, "Test Song")
        self.assertEqual(song.album_title, "Test Album")
        self.assertEqual(song.artist_name, "Test Artist")
        self.assertEqual(song.genre_name, "Rock")
        self.assertEqual(song.duration_seconds, 180)
        self.assertEqual(song.track_number, 1)
        self.assertEqual(song.play_count, 100)
        self.assertEqual(song.favorite_count, 10)
        self.assertEqual(song.download_count, 5)
        self.assertFalse(song.is_explicit)
        self.assertTrue(song.is_active)
        self.assertFalse(song.is_premium)
        self.assertEqual(song.source_type, "youtube")

        # Verificar que tiene timestamps
        self.assertIsNotNone(song.created_at)
        self.assertIsNotNone(song.updated_at)

    def test_create_song_with_minimal_data(self):
        """Test crear canción con datos mínimos requeridos"""
        minimal_song = Song.objects.create(title="Minimal Song")

        # Verificar valores por defecto
        self.assertEqual(minimal_song.title, "Minimal Song")
        self.assertEqual(minimal_song.duration_seconds, 0)
        self.assertEqual(minimal_song.play_count, 0)
        self.assertEqual(minimal_song.favorite_count, 0)
        self.assertEqual(minimal_song.download_count, 0)
        self.assertEqual(minimal_song.tags, [])
        self.assertEqual(minimal_song.source_type, "youtube")
        self.assertEqual(minimal_song.audio_quality, "standard")
        self.assertTrue(minimal_song.is_active)
        self.assertFalse(minimal_song.is_explicit)
        self.assertFalse(minimal_song.is_premium)

    def test_song_title_required(self):
        """Test que el título es requerido"""
        with self.assertRaises(IntegrityError):
            Song.objects.create(title=None)

    def test_song_title_max_length(self):
        """Test longitud máxima del título"""
        long_title = "x" * 256  # Más de 255 caracteres

        with self.assertRaises(ValidationError):
            song = Song(title=long_title)
            song.full_clean()

    def test_song_duration_validation(self):
        """Test validación de duración"""
        # Duración negativa
        with self.assertRaises(ValidationError):
            song = Song(title="Test", duration_seconds=-1)
            song.full_clean()

        # Duración muy alta (más de 24 horas)
        with self.assertRaises(ValidationError):
            song = Song(title="Test", duration_seconds=86401)
            song.full_clean()

        # Duración válida
        song = Song(title="Test", duration_seconds=3600)  # 1 hora
        song.full_clean()  # No debería lanzar excepción

    def test_song_counters_positive(self):
        """Test que los contadores no pueden ser negativos"""
        song_data = self.valid_song_data.copy()

        # Test play_count negativo
        song_data["play_count"] = -1
        with self.assertRaises(ValidationError):
            song = Song(**song_data)
            song.full_clean()

        # Test favorite_count negativo
        song_data["play_count"] = 0
        song_data["favorite_count"] = -1
        with self.assertRaises(ValidationError):
            song = Song(**song_data)
            song.full_clean()

        # Test download_count negativo
        song_data["favorite_count"] = 0
        song_data["download_count"] = -1
        with self.assertRaises(ValidationError):
            song = Song(**song_data)
            song.full_clean()

    def test_song_track_number_positive(self):
        """Test que el número de track debe ser positivo"""
        with self.assertRaises(ValidationError):
            song = Song(title="Test", track_number=-1)
            song.full_clean()

        # Track number 0 también debería ser inválido para PositiveIntegerField
        with self.assertRaises(ValidationError):
            song = Song(title="Test", track_number=0)
            song.full_clean()

    def test_song_urls_validation(self):
        """Test validación de URLs"""
        # URL válida
        song = Song(
            title="Test",
            file_url="https://example.com/song.mp3",
            thumbnail_url="https://example.com/thumb.jpg",
        )
        song.full_clean()  # No debería lanzar excepción

        # URL inválida
        with self.assertRaises(ValidationError):
            song = Song(title="Test", file_url="not-a-url")
            song.full_clean()

    def test_song_tags_json_field(self):
        """Test campo JSON tags"""
        # Tags como lista
        song = Song.objects.create(
            title="Test with Tags", tags=["rock", "classic", "guitar"]
        )
        self.assertEqual(song.tags, ["rock", "classic", "guitar"])

        # Tags vacío por defecto
        song_empty = Song.objects.create(title="No Tags")
        self.assertEqual(song_empty.tags, [])

        # Tags como diccionario también debería funcionar
        song_dict = Song.objects.create(
            title="Test with Dict Tags", tags={"genres": ["rock"], "mood": ["happy"]}
        )
        self.assertIsInstance(song_dict.tags, dict)

    def test_song_source_type_choices(self):
        """Test choices del source_type"""
        valid_sources = ["youtube", "upload", "spotify", "other"]

        for source in valid_sources:
            song = Song(title=f"Test {source}", source_type=source)
            song.full_clean()  # No debería lanzar excepción

    def test_song_audio_quality_choices(self):
        """Test choices de audio_quality"""
        valid_qualities = ["standard", "high", "lossless"]

        for quality in valid_qualities:
            song = Song(title=f"Test {quality}", audio_quality=quality)
            song.full_clean()  # No debería lanzar excepción

    def test_song_boolean_fields(self):
        """Test campos booleanos"""
        song = Song.objects.create(
            title="Boolean Test", is_explicit=True, is_active=False, is_premium=True
        )

        self.assertTrue(song.is_explicit)
        self.assertFalse(song.is_active)
        self.assertTrue(song.is_premium)

    def test_song_str_representation(self):
        """Test representación string del modelo"""
        song = Song.objects.create(title="Test Song", artist_name="Test Artist")

        # Asumiendo que el modelo tiene un método __str__
        expected = f"{song.artist_name} - {song.title}"
        # Si no tiene __str__ personalizado, usará el default
        str_representation = str(song)
        self.assertIn("Test Song", str_representation)

    def test_song_database_indexes(self):
        """Test que los índices de BD están configurados"""
        # Este test es más conceptual, verificamos que los campos
        # con db_index=True estén definidos correctamente
        song = Song.objects.create(**self.valid_song_data)

        # Verificar que podemos hacer queries eficientes en campos indexados
        songs_by_album = Song.objects.filter(album_id=song.album_id)
        songs_by_artist = Song.objects.filter(artist_id=song.artist_id)
        songs_by_genre = Song.objects.filter(genre_id=song.genre_id)
        songs_by_album_title = Song.objects.filter(album_title=song.album_title)
        songs_by_artist_name = Song.objects.filter(artist_name=song.artist_name)
        songs_by_genre_name = Song.objects.filter(genre_name=song.genre_name)
        songs_by_play_count = Song.objects.filter(play_count__gte=50)

        # Todos deberían encontrar nuestra canción
        self.assertIn(song, songs_by_album)
        self.assertIn(song, songs_by_artist)
        self.assertIn(song, songs_by_genre)
        self.assertIn(song, songs_by_album_title)
        self.assertIn(song, songs_by_artist_name)
        self.assertIn(song, songs_by_genre_name)
        self.assertIn(song, songs_by_play_count)

    def test_song_uuid_generation(self):
        """Test que el UUID se genera automáticamente"""
        song1 = Song.objects.create(title="Song 1")
        song2 = Song.objects.create(title="Song 2")

        # Ambas deben tener UUIDs únicos
        self.assertIsInstance(song1.id, uuid.UUID)
        self.assertIsInstance(song2.id, uuid.UUID)
        self.assertNotEqual(song1.id, song2.id)

    def test_song_lyrics_text_field(self):
        """Test campo de texto para lyrics"""
        long_lyrics = (
            """Verse 1:
This is a very long song
With multiple verses and choruses
That should test the TextField capability

Chorus:
Long text should be stored properly
In the database without issues
Text fields can handle large content

Verse 2:
Another verse with more content
To ensure everything works fine
"""
            * 10
        )  # Multiplicar para hacer más largo

        song = Song.objects.create(title="Long Lyrics Song", lyrics=long_lyrics)

        self.assertEqual(song.lyrics, long_lyrics)
        self.assertGreater(len(song.lyrics), 1000)


if __name__ == "__main__":
    unittest.main()
