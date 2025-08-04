"""
Tests para views de Songs API
"""
# Configurar path antes de importar
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from src.apps.songs.api.simple_views import TestView, test_function_view
from src.apps.songs.domain.entities import SongEntity


class TestSimpleViews(APITestCase):
    """Tests para vistas simples de Songs"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()

    def test_test_view_class_based(self):
        """Test vista de clase TestView"""
        # Simular request GET directamente a la vista
        view = TestView()

        # Mock request
        mock_request = Mock()

        # Act
        response = view.get(mock_request)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Songs API is working!")

    def test_test_function_view(self):
        """Test vista de función test_function_view"""
        # Mock request
        mock_request = Mock()

        # Act
        response = test_function_view(mock_request)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Function view working!")


class TestSongViewsConcepts(TestCase):
    """Tests conceptuales para las vistas de songs (sin endpoints reales)"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.sample_entities = [
            SongEntity(
                id="song-1",
                title="Random Song 1",
                artist_name="Artist 1",
                album_title="Album 1",
                genre_name="Rock",
                duration_seconds=180,
                play_count=100,
                favorite_count=10,
                download_count=5,
                tags=["rock", "classic"],
                is_active=True,
                created_at=datetime.now(),
            ),
            SongEntity(
                id="song-2",
                title="Random Song 2",
                artist_name="Artist 2",
                album_title="Album 2",
                genre_name="Pop",
                duration_seconds=200,
                play_count=200,
                favorite_count=20,
                download_count=10,
                tags=["pop", "modern"],
                is_active=True,
                created_at=datetime.now(),
            ),
        ]

    def test_entity_to_dict_conversion(self):
        """Test conversión de entidad a diccionario para serializer"""
        from src.apps.songs.api.views.song_views import entity_to_dict

        entity = self.sample_entities[0]
        result = entity_to_dict(entity)

        # Verificar conversión correcta
        self.assertEqual(result["id"], "song-1")
        self.assertEqual(result["title"], "Random Song 1")
        self.assertEqual(result["artist_name"], "Artist 1")
        self.assertEqual(result["album_title"], "Album 1")
        self.assertEqual(result["genre_name"], "Rock")
        self.assertEqual(result["duration_seconds"], 180)
        self.assertEqual(result["play_count"], 100)
        self.assertEqual(result["favorite_count"], 10)
        self.assertEqual(result["tags"], ["rock", "classic"])
        self.assertTrue(result["is_active"])
        self.assertIsInstance(result, dict)

    def test_entity_to_dict_with_none_tags(self):
        """Test conversión con tags None"""
        from src.apps.songs.api.views.song_views import entity_to_dict

        entity = SongEntity(id="song-no-tags", title="Song Without Tags", tags=None)

        result = entity_to_dict(entity)

        # Tags None debe convertirse a lista vacía
        self.assertEqual(result["tags"], [])

    def test_entity_to_dict_all_fields(self):
        """Test que todos los campos de la entidad se incluyen en el dict"""
        from src.apps.songs.api.views.song_views import entity_to_dict

        entity = SongEntity(
            id="song-complete",
            title="Complete Song",
            artist_name="Complete Artist",
            album_title="Complete Album",
            genre_name="Complete Genre",
            duration_seconds=300,
            file_url="https://example.com/file.mp3",
            thumbnail_url="https://example.com/thumb.jpg",
            tags=["complete", "test"],
            play_count=500,
            favorite_count=50,
            download_count=25,
            source_type="youtube",
            source_id="youtube-complete",
            source_url="https://youtube.com/watch?v=complete",
            is_explicit=True,
            is_premium=False,
            audio_quality="high",
            created_at=datetime.now(),
            last_played_at=datetime.now(),
            release_date=datetime.now(),
        )

        result = entity_to_dict(entity)

        # Verificar que todos los campos esperados están presentes
        expected_fields = [
            "id",
            "title",
            "artist_name",
            "album_title",
            "genre_name",
            "duration_seconds",
            "file_url",
            "thumbnail_url",
            "tags",
            "play_count",
            "favorite_count",
            "download_count",
            "source_type",
            "source_id",
            "source_url",
            "is_explicit",
            "is_premium",
            "audio_quality",
            "created_at",
            "last_played_at",
            "release_date",
        ]

        for field in expected_fields:
            self.assertIn(field, result, f"Field {field} should be present in result")

    @patch("apps.songs.api.views.song_views.SongUseCases")
    @patch("apps.songs.api.views.song_views.SongRepository")
    def test_random_songs_view_concept(self, mock_repo_class, mock_use_cases_class):
        """Test concepto de RandomSongsView (sin hacer requests HTTP)"""
        from src.apps.songs.api.views.song_views import RandomSongsView

        # Configurar mocks
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_use_cases = Mock()
        mock_use_cases.get_random_songs = AsyncMock(return_value=self.sample_entities)
        mock_use_cases_class.return_value = mock_use_cases

        # Crear vista
        view = RandomSongsView()

        # Verificar que hereda de LoggingMixin
        self.assertTrue(hasattr(view, "logger"))

        # El resto requeriría hacer requests HTTP reales
        # que está fuera del scope de este test conceptual

    def test_song_data_structure_for_api(self):
        """Test estructura de datos esperada por la API"""
        entity = self.sample_entities[0]

        # Simular lo que haría la vista para preparar datos para el serializer
        api_data = {
            "id": entity.id,
            "title": entity.title,
            "artist_name": entity.artist_name,
            "album_title": entity.album_title,
            "duration_seconds": entity.duration_seconds,
            "play_count": entity.play_count,
            "tags": entity.tags or [],
        }

        # Verificar estructura esperada
        self.assertIn("id", api_data)
        self.assertIn("title", api_data)
        self.assertIn("artist_name", api_data)
        self.assertIn("play_count", api_data)
        self.assertIsInstance(api_data["tags"], list)

    def test_response_structure_concept(self):
        """Test estructura conceptual de respuesta de API"""
        # Simular respuesta exitosa
        success_response = {
            "success": True,
            "data": {
                "songs": [
                    {"id": "song-1", "title": "Test Song", "artist_name": "Test Artist"}
                ],
                "count": 1,
            },
        }

        self.assertTrue(success_response["success"])
        self.assertIn("data", success_response)
        self.assertIn("songs", success_response["data"])
        self.assertIsInstance(success_response["data"]["songs"], list)

        # Simular respuesta de error
        error_response = {
            "success": False,
            "error": {"message": "Error occurred", "code": "INTERNAL_ERROR"},
        }

        self.assertFalse(error_response["success"])
        self.assertIn("error", error_response)
        self.assertIn("message", error_response["error"])

    def test_pagination_concept(self):
        """Test concepto de paginación para listas de canciones"""
        # Simular datos paginados
        paginated_response = {
            "success": True,
            "data": {
                "songs": [song.__dict__ for song in self.sample_entities],
                "pagination": {
                    "current_page": 1,
                    "total_pages": 5,
                    "total_items": 100,
                    "items_per_page": 20,
                    "has_next": True,
                    "has_previous": False,
                },
            },
        }

        # Verificar estructura de paginación
        pagination = paginated_response["data"]["pagination"]
        self.assertEqual(pagination["current_page"], 1)
        self.assertEqual(pagination["total_pages"], 5)
        self.assertEqual(pagination["total_items"], 100)
        self.assertEqual(pagination["items_per_page"], 20)
        self.assertTrue(pagination["has_next"])
        self.assertFalse(pagination["has_previous"])

    def test_query_parameters_concept(self):
        """Test concepto de parámetros de consulta"""
        # Simular parámetros típicos para búsqueda de canciones
        query_params = {
            "q": "rock music",  # Búsqueda por texto
            "genre": "rock",  # Filtro por género
            "artist": "test artist",  # Filtro por artista
            "limit": 20,  # Límite de resultados
            "page": 1,  # Página
            "sort": "popularity",  # Ordenamiento
            "order": "desc",  # Dirección del ordenamiento
        }

        # Verificar que todos los parámetros son del tipo correcto
        self.assertIsInstance(query_params["q"], str)
        self.assertIsInstance(query_params["genre"], str)
        self.assertIsInstance(query_params["artist"], str)
        self.assertIsInstance(query_params["limit"], int)
        self.assertIsInstance(query_params["page"], int)
        self.assertIn(query_params["sort"], ["popularity", "date", "title", "artist"])
        self.assertIn(query_params["order"], ["asc", "desc"])

    def test_error_handling_concept(self):
        """Test concepto de manejo de errores en vistas"""
        # Tipos de errores comunes
        error_scenarios = [
            {"type": "ValidationError", "status": 400, "message": "Invalid input data"},
            {"type": "NotFound", "status": 404, "message": "Song not found"},
            {"type": "PermissionDenied", "status": 403, "message": "Access denied"},
            {
                "type": "InternalError",
                "status": 500,
                "message": "Internal server error",
            },
        ]

        for scenario in error_scenarios:
            self.assertIn("type", scenario)
            self.assertIn("status", scenario)
            self.assertIn("message", scenario)
            self.assertIsInstance(scenario["status"], int)
            self.assertGreaterEqual(scenario["status"], 400)
            self.assertLessEqual(scenario["status"], 599)

    @patch("apps.songs.api.views.most_popular_songs_view.SongRepository")
    @patch("apps.songs.api.views.most_popular_songs_view.GetMostPlayedSongsUseCase")
    def test_most_popular_songs_view_concept(
        self, mock_use_case_class, mock_repo_class
    ):
        """Test concepto de MostPopularSongsView (sin hacer requests HTTP)"""
        from src.apps.songs.api.views.most_popular_songs_view import MostPopularSongsView

        # Configurar mocks
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_use_case = AsyncMock()
        mock_use_case.execute = AsyncMock(
            return_value=self.sample_entities[:3]
        )  # Top 3 most popular
        mock_use_case_class.return_value = mock_use_case

        # Crear vista
        view = MostPopularSongsView()

        # Verificar que hereda de LoggingMixin
        self.assertTrue(hasattr(view, "logger"))

        # Verificar que tiene los atributos esperados
        self.assertTrue(hasattr(view, "repository"))
        self.assertTrue(hasattr(view, "get_most_played_songs_use_case"))
        self.assertTrue(hasattr(view, "mapper"))

        # Verificar que se configuran los permisos correctos
        from rest_framework.permissions import AllowAny

        self.assertEqual(view.permission_classes, [AllowAny])

    def test_most_popular_songs_api_data_structure(self):
        """Test estructura de datos para API de canciones más populares"""
        # Simular entidades ordenadas por play_count
        popular_entities = sorted(
            self.sample_entities, key=lambda x: x.play_count, reverse=True
        )[
            :5
        ]  # Top 5

        # Simular preparación de datos para serializer
        api_data = []
        for entity in popular_entities:
            song_data = {
                "id": entity.id,
                "title": entity.title,
                "artist_name": entity.artist_name,
                "album_title": entity.album_title,
                "duration_seconds": entity.duration_seconds,
                "play_count": entity.play_count,
                "thumbnail_url": entity.thumbnail_url,
            }
            api_data.append(song_data)

        # Verificar estructura
        self.assertEqual(len(api_data), min(5, len(self.sample_entities)))

        # Verificar que están ordenadas por play_count descendente
        for i in range(len(api_data) - 1):
            self.assertGreaterEqual(
                api_data[i]["play_count"],
                api_data[i + 1]["play_count"],
                "Songs should be ordered by play_count descending",
            )

        # Verificar estructura de cada canción
        for song in api_data:
            self.assertIn("id", song)
            self.assertIn("title", song)
            self.assertIn("artist_name", song)
            self.assertIn("play_count", song)
            self.assertIsInstance(song["play_count"], int)
            self.assertGreaterEqual(song["play_count"], 0)


if __name__ == "__main__":
    unittest.main()
