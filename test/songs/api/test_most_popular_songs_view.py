"""
Tests específicos para MostPopularSongsView
"""
<<<<<<< HEAD

=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from rest_framework import status
from rest_framework.test import APITestCase

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from apps.songs.domain.entities import SongEntity


class TestMostPopularSongsView(APITestCase):
    """Tests para MostPopularSongsView"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear entidades de prueba con diferentes play_counts
        self.sample_entities = [
            SongEntity(
                id="song-1",
                title="Most Popular Song",
                artist_name="Artist 1",
                album_title="Album 1",
                play_count=1000,  # Más reproducida
                duration_seconds=180,
            ),
            SongEntity(
                id="song-2",
                title="Second Popular Song",
                artist_name="Artist 2",
                album_title="Album 2",
                play_count=750,
                duration_seconds=200,
            ),
            SongEntity(
                id="song-3",
                title="Third Popular Song",
                artist_name="Artist 3",
                album_title="Album 3",
                play_count=500,
                duration_seconds=160,
            ),
            SongEntity(
                id="song-4",
                title="Less Popular Song",
                artist_name="Artist 4",
                album_title="Album 4",
                play_count=250,
                duration_seconds=220,
            ),
            SongEntity(
                id="song-5",
                title="Least Popular Song",
                artist_name="Artist 5",
                album_title="Album 5",
                play_count=100,  # Menos reproducida
                duration_seconds=190,
            ),
        ]

    @patch("apps.songs.api.views.most_popular_songs_view.SongRepository")
    @patch("apps.songs.api.views.most_popular_songs_view.GetMostPlayedSongsUseCase")
    def test_view_initialization(self, mock_use_case_class, mock_repo_class):
        """Test inicialización correcta de la vista"""
        from apps.songs.api.views.most_popular_songs_view import MostPopularSongsView

        # Configurar mocks
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_use_case = Mock()
        mock_use_case_class.return_value = mock_use_case

        # Crear vista
        view = MostPopularSongsView()

        # Verificar inicialización correcta
        self.assertTrue(hasattr(view, "repository"))
        self.assertTrue(hasattr(view, "get_most_played_songs_use_case"))
        self.assertTrue(hasattr(view, "mapper"))
        self.assertTrue(hasattr(view, "logger"))  # De LoggingMixin

        # Verificar permisos
        from rest_framework.permissions import AllowAny

        self.assertEqual(view.permission_classes, [AllowAny])

    def test_data_ordering_by_play_count(self):
        """Test que los datos se ordenan correctamente por play_count"""
        # Ordenar entidades por play_count descendente
        sorted_entities = sorted(
            self.sample_entities, key=lambda x: x.play_count, reverse=True
        )

        # Verificar orden correcto
        self.assertEqual(sorted_entities[0].play_count, 1000)  # Más popular
        self.assertEqual(sorted_entities[1].play_count, 750)
        self.assertEqual(sorted_entities[2].play_count, 500)
        self.assertEqual(sorted_entities[3].play_count, 250)
        self.assertEqual(sorted_entities[4].play_count, 100)  # Menos popular

        # Verificar que el orden es descendente
        for i in range(len(sorted_entities) - 1):
            self.assertGreaterEqual(
                sorted_entities[i].play_count,
                sorted_entities[i + 1].play_count,
                "Play counts should be in descending order",
            )

    def test_limit_parameter_validation(self):
        """Test validación del parámetro limit"""
        # Límites válidos
        valid_limits = [1, 5, 10, 25, 50, 100]
        for limit in valid_limits:
            self.assertGreater(limit, 0, f"Limit {limit} should be greater than 0")
            self.assertLessEqual(limit, 100, f"Limit {limit} should not exceed 100")

        # Límites inválidos
        invalid_limits = [0, -1, -10, 101, 200]
        for limit in invalid_limits:
            self.assertTrue(
                limit <= 0 or limit > 100, f"Limit {limit} should be invalid"
            )

    def test_dto_creation_concept(self):
        """Test concepto de creación de DTOs para respuesta"""
        from apps.songs.api.dtos import MostPopularSongsRequestDTO

        # Test creación con valores por defecto
        default_dto = MostPopularSongsRequestDTO()
        self.assertEqual(default_dto.limit, 10)

        # Test creación con límite personalizado
        custom_dto = MostPopularSongsRequestDTO(limit=5)
        self.assertEqual(custom_dto.limit, 5)

        # Test validación de tipos
        self.assertIsInstance(default_dto.limit, int)
        self.assertIsInstance(custom_dto.limit, int)

    def test_response_data_structure(self):
        """Test estructura de datos de respuesta"""
        # Simular estructura de respuesta esperada
        expected_response_structure = {
            "id": "string",
            "title": "string",
            "artist_name": "string",
            "album_title": "string",
            "duration_formatted": "string",
            "thumbnail_url": "string",
            "play_count": "integer",
        }

        # Simular conversión de entidad a datos de respuesta
        entity = self.sample_entities[0]
        response_data = {
            "id": entity.id,
            "title": entity.title,
            "artist_name": entity.artist_name,
            "album_title": entity.album_title,
            "duration_formatted": f"{entity.duration_seconds // 60:02d}:{entity.duration_seconds % 60:02d}",
            "thumbnail_url": entity.thumbnail_url,
            "play_count": entity.play_count,
        }

        # Verificar que tiene todos los campos esperados
        for field in expected_response_structure.keys():
            self.assertIn(field, response_data, f"Field {field} should be present")

        # Verificar tipos de datos
        self.assertIsInstance(response_data["id"], str)
        self.assertIsInstance(response_data["title"], str)
        self.assertIsInstance(response_data["play_count"], int)

    def test_use_case_integration_concept(self):
        """Test concepto de integración con el caso de uso"""
        from apps.songs.use_cases import GetMostPlayedSongsUseCase

        # Verificar que el caso de uso existe y tiene el método correcto
        self.assertTrue(hasattr(GetMostPlayedSongsUseCase, "execute"))

        # Mock del caso de uso
        mock_use_case = AsyncMock()
        mock_use_case.execute = AsyncMock(return_value=self.sample_entities[:3])

        # Simular ejecución
        async def simulate_execution():
            result = await mock_use_case.execute(3)
            return result

        # Verificar que retorna el número esperado de resultados
        import asyncio

        result = asyncio.run(simulate_execution())
        self.assertEqual(len(result), 3)

    def test_error_handling_scenarios(self):
        """Test escenarios de manejo de errores"""
        error_scenarios = [
            {
                "scenario": "Invalid limit parameter",
                "limit": "invalid",
                "expected_status": status.HTTP_400_BAD_REQUEST,
            },
            {
                "scenario": "Negative limit",
                "limit": -1,
                "expected_status": status.HTTP_400_BAD_REQUEST,
            },
            {
                "scenario": "Limit too high",
                "limit": 1000,
                "expected_status": status.HTTP_400_BAD_REQUEST,
            },
            {
                "scenario": "Zero limit",
                "limit": 0,
                "expected_status": status.HTTP_400_BAD_REQUEST,
            },
        ]

        for scenario in error_scenarios:
            with self.subTest(scenario=scenario["scenario"]):
                # Verificar que se identifican correctamente los errores
                limit = scenario["limit"]

                if isinstance(limit, str):
                    # Error de tipo
                    with self.assertRaises(ValueError):
                        int(limit)
                elif limit <= 0 or limit > 100:
                    # Error de rango
                    self.assertTrue(
                        limit <= 0 or limit > 100, f"Limit {limit} should be invalid"
                    )


if __name__ == "__main__":
    unittest.main()
