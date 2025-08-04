"""
Tests para serializers de Songs API
"""

# Configurar path antes de importar
import sys
import unittest
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from apps.songs.api.serializers.song_serializers import (
    SongListSerializer,
    SongSerializer,
)


class TestSongSerializer(unittest.TestCase):
    """Tests para SongSerializer"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.valid_song_data = {
            "id": str(uuid.uuid4()),
            "title": "Test Song",
            "youtube_video_id": "dQw4w9WgXcQ",
            "artist_name": "Test Artist",
            "album_title": "Test Album",
            "genre_name": "Rock",
            "duration_seconds": 180,
            "file_url": "https://example.com/song.mp3",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "youtube_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "tags": ["rock", "classic", "guitar"],
            "play_count": 100,
            "youtube_view_count": 1000000,
            "youtube_like_count": 50000,
            "is_explicit": False,
            "audio_downloaded": True,
            "created_at": datetime.now(),
            "published_at": datetime.now(),
        }

        self.mock_song_object = type("MockSong", (), self.valid_song_data)()

    def test_serialize_song_with_valid_data(self):
        """Test serialización de canción con datos válidos"""
        serializer = SongSerializer(data=self.valid_song_data)

        # Verificar que los datos son válidos
        self.assertTrue(serializer.is_valid(), f"Errors: {serializer.errors}")

        # Verificar campos serializados
        validated_data = serializer.validated_data
        self.assertEqual(validated_data["title"], "Test Song")
        self.assertEqual(validated_data["youtube_video_id"], "dQw4w9WgXcQ")
        self.assertEqual(validated_data["artist_name"], "Test Artist")
        self.assertEqual(validated_data["duration_seconds"], 180)
        self.assertEqual(validated_data["play_count"], 100)
        self.assertEqual(validated_data["tags"], ["rock", "classic", "guitar"])
        self.assertFalse(validated_data["is_explicit"])
        self.assertTrue(validated_data["audio_downloaded"])

    def test_serialize_song_duration_formatted(self):
        """Test campo calculado duration_formatted"""
        # Test con objeto mock
        serializer = SongSerializer(self.mock_song_object)
        data = serializer.data

        # 180 segundos = 3:00
        self.assertEqual(data["duration_formatted"], "03:00")

        # Test con diferentes duraciones
        test_cases = [
            (0, "00:00"),
            (30, "00:30"),
            (60, "01:00"),
            (90, "01:30"),
            (3661, "61:01"),  # Más de 1 hora
        ]

        for duration, expected in test_cases:
            with self.subTest(duration=duration):
                obj = type("TestSong", (), {"duration_seconds": duration})()
                serializer = SongSerializer(obj)
                self.assertEqual(serializer.data["duration_formatted"], expected)

    def test_serialize_song_with_null_optional_fields(self):
        """Test serialización con campos opcionales nulos"""
        data = self.valid_song_data.copy()
        data.update(
            {
                "artist_name": None,
                "album_title": None,
                "genre_name": None,
                "file_url": None,
                "thumbnail_url": None,
                "published_at": None,
            }
        )

        serializer = SongSerializer(data=data)
        self.assertTrue(serializer.is_valid(), f"Errors: {serializer.errors}")

        validated_data = serializer.validated_data
        self.assertIsNone(validated_data["artist_name"])
        self.assertIsNone(validated_data["album_title"])
        self.assertIsNone(validated_data["genre_name"])
        self.assertIsNone(validated_data["file_url"])
        self.assertIsNone(validated_data["thumbnail_url"])
        self.assertIsNone(validated_data["published_at"])

    def test_serialize_song_with_empty_tags(self):
        """Test serialización con tags vacíos"""
        data = self.valid_song_data.copy()
        data["tags"] = []

        serializer = SongSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        validated_data = serializer.validated_data
        self.assertEqual(validated_data["tags"], [])

    def test_serialize_song_missing_required_fields(self):
        """Test validación con campos requeridos faltantes"""
        required_fields = [
            "title",
            "youtube_video_id",
            "duration_seconds",
            "youtube_url",
            "play_count",
            "youtube_view_count",
            "youtube_like_count",
            "is_explicit",
            "audio_downloaded",
        ]

        for field in required_fields:
            with self.subTest(missing_field=field):
                data = self.valid_song_data.copy()
                del data[field]

                serializer = SongSerializer(data=data)
                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)

    def test_serialize_song_invalid_data_types(self):
        """Test validación con tipos de datos inválidos"""
        test_cases = [
            ("duration_seconds", -1, "Debe ser >= 0"),
            ("duration_seconds", "invalid", "Debe ser entero"),
            ("play_count", -5, "Debe ser >= 0"),
            ("youtube_view_count", "invalid", "Debe ser entero"),
            ("youtube_like_count", -10, "Debe ser >= 0"),
            ("file_url", "not-a-url", "Debe ser URL válida"),
            ("thumbnail_url", "invalid-url", "Debe ser URL válida"),
            ("youtube_url", "bad-url", "Debe ser URL válida"),
            ("is_explicit", "not-boolean", "Debe ser booleano"),
            ("audio_downloaded", "invalid", "Debe ser booleano"),
        ]

        for field, invalid_value, description in test_cases:
            with self.subTest(field=field, value=invalid_value):
                data = self.valid_song_data.copy()
                data[field] = invalid_value

                serializer = SongSerializer(data=data)
                self.assertFalse(
                    serializer.is_valid(),
                    f"Field {field} should be invalid: {description}",
                )
                self.assertIn(field, serializer.errors)

    def test_serialize_song_title_max_length(self):
        """Test validación de longitud máxima del título"""
        data = self.valid_song_data.copy()
        data["title"] = "x" * 256  # Más de 255 caracteres

        serializer = SongSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_serialize_song_youtube_video_id_max_length(self):
        """Test validación de longitud del youtube_video_id"""
        data = self.valid_song_data.copy()
        data["youtube_video_id"] = "x" * 21  # Más de 20 caracteres

        serializer = SongSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("youtube_video_id", serializer.errors)

    def test_serialize_song_tags_validation(self):
        """Test validación del campo tags"""
        # Tags válidos
        valid_tags_cases = [
            [],
            ["rock"],
            ["rock", "classic", "guitar"],
            ["very-long-tag-but-under-50-chars"],
        ]

        for tags in valid_tags_cases:
            with self.subTest(tags=tags):
                data = self.valid_song_data.copy()
                data["tags"] = tags

                serializer = SongSerializer(data=data)
                self.assertTrue(serializer.is_valid(), f"Tags should be valid: {tags}")

        # Tags inválidos
        data = self.valid_song_data.copy()
        data["tags"] = ["x" * 51]  # Tag más largo de 50 caracteres

        serializer = SongSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("tags", serializer.errors)


class TestSongListSerializer(unittest.TestCase):
    """Tests para SongListSerializer"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.valid_list_data = {
            "id": str(uuid.uuid4()),
            "title": "List Song",
            "artist_name": "List Artist",
            "album_title": "List Album",
            "duration_seconds": 200,
            "thumbnail_url": "https://example.com/list-thumb.jpg",
            "play_count": 50,
        }

        self.mock_list_object = type("MockListSong", (), self.valid_list_data)()

    def test_serialize_song_list_with_valid_data(self):
        """Test serialización de lista de canciones"""
        serializer = SongListSerializer(data=self.valid_list_data)

        self.assertTrue(serializer.is_valid(), f"Errors: {serializer.errors}")

        validated_data = serializer.validated_data
        self.assertEqual(validated_data["title"], "List Song")
        self.assertEqual(validated_data["artist_name"], "List Artist")
        self.assertEqual(validated_data["album_title"], "List Album")
        self.assertEqual(validated_data["play_count"], 50)

    def test_serialize_song_list_duration_formatted(self):
        """Test campo calculado duration_formatted en lista"""
        serializer = SongListSerializer(self.mock_list_object)
        data = serializer.data

        # 200 segundos = 3:20
        self.assertEqual(data["duration_formatted"], "03:20")

    def test_serialize_song_list_with_null_optionals(self):
        """Test serialización de lista con campos opcionales nulos"""
        data = self.valid_list_data.copy()
        data.update({"artist_name": None, "album_title": None, "thumbnail_url": None})

        serializer = SongListSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        validated_data = serializer.validated_data
        self.assertIsNone(validated_data["artist_name"])
        self.assertIsNone(validated_data["album_title"])
        self.assertIsNone(validated_data["thumbnail_url"])

    def test_serialize_song_list_required_fields(self):
        """Test campos requeridos en SongListSerializer"""
        required_fields = ["id", "title", "play_count"]

        for field in required_fields:
            with self.subTest(missing_field=field):
                data = self.valid_list_data.copy()
                del data[field]

                serializer = SongListSerializer(data=data)
                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)

    def test_compare_serializers_field_subset(self):
        """Test que SongListSerializer es un subconjunto de SongSerializer"""
        # Campos en SongListSerializer
        list_serializer = SongListSerializer()
        list_fields = set(list_serializer.fields.keys())

        # Campos en SongSerializer
        full_serializer = SongSerializer()
        full_fields = set(full_serializer.fields.keys())

        # Verificar que los campos comunes tienen el mismo tipo (excepto SerializerMethodField)
        common_fields = list_fields.intersection(full_fields)

        for field_name in common_fields:
            if (
                field_name != "duration_formatted"
            ):  # Este es SerializerMethodField en ambos
                list_field = list_serializer.fields[field_name]
                full_field = full_serializer.fields[field_name]

                # Verificar que son del mismo tipo
                self.assertEqual(
                    type(list_field),
                    type(full_field),
                    f"Field {field_name} should have same type in both serializers",
                )


if __name__ == "__main__":
    unittest.main()
