"""
Tests para casos de uso de búsqueda de canciones
"""
# Configurar path antes de importar
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from src.apps.songs.domain.entities import SongEntity
from src.apps.songs.use_cases.song_use_cases import SongUseCases


class TestSearchSongs(unittest.IsolatedAsyncioTestCase):
    """Tests para el caso de uso search_songs"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Mock del repositorio
        self.mock_repository = Mock()
        self.mock_repository.search = AsyncMock()
        self.mock_repository.get_by_source = AsyncMock()
        self.mock_repository.create = AsyncMock()

        # Instancia del caso de uso
        self.song_use_cases = SongUseCases(self.mock_repository)

        # Mock del music service
        self.song_use_cases.music_service = Mock()
        self.song_use_cases.music_service.search_and_process_music = AsyncMock()

        # Datos de prueba
        self.sample_songs = [
            SongEntity(
                id=f"song-{i}",
                title=f"Rock Song {i}",
                artist_name=f"Rock Artist {i}",
                album_title=f"Rock Album {i}",
                genre_name="Rock",
                duration_seconds=180,
                is_active=True,
            )
            for i in range(1, 6)
        ]

        # Mock track data de YouTube
        self.mock_track_data = Mock()
        self.mock_track_data.video_id = "youtube-search-123"
        self.mock_track_data.title = "YouTube Search Result"
        self.mock_track_data.artist = "YouTube Artist"
        self.mock_track_data.duration = 200

    async def test_search_songs_local_sufficient_results(self):
        """Test búsqueda con suficientes resultados locales"""
        # Arrange
        query = "rock"
        limit = 20
        local_results = self.sample_songs[:3]

        self.mock_repository.search.return_value = local_results

        # Act
        result = await self.song_use_cases.search_songs(query=query, limit=limit)

        # Assert
        self.assertEqual(len(result), 3)
        self.assertEqual(result, local_results)
        self.mock_repository.search.assert_called_once_with(query, limit)
        # No debe buscar en YouTube si hay suficientes resultados locales
        self.song_use_cases.music_service.search_and_process_music.assert_not_called()

    async def test_search_songs_local_insufficient_search_youtube(self):
        """Test búsqueda con pocos resultados locales, busca en YouTube"""
        # Arrange
        query = "rare song"
        limit = 20
        local_results = self.sample_songs[:2]  # Solo 2 resultados locales
        youtube_tracks = [self.mock_track_data]

        self.mock_repository.search.return_value = local_results
        self.song_use_cases.music_service.search_and_process_music.return_value = (
            youtube_tracks
        )
        self.mock_repository.get_by_source.return_value = None  # No existe

        # Mock para _save_track_as_song
        new_song = SongEntity(
            id="new-search-song",
            title="YouTube Search Result",
            artist_name="YouTube Artist",
            source_type="youtube",
            source_id="youtube-search-123",
        )

        with patch.object(
            self.song_use_cases, "_save_track_as_song", return_value=new_song
        ):
            # Act
            result = await self.song_use_cases.search_songs(query=query, limit=limit)

            # Assert
            self.assertGreaterEqual(len(result), len(local_results))
            self.song_use_cases.music_service.search_and_process_music.assert_called_once_with(
                query, limit - len(local_results)
            )
            self.assertIn(new_song, result)

    async def test_search_songs_disable_youtube_search(self):
        """Test búsqueda con YouTube deshabilitado"""
        # Arrange
        query = "test"
        limit = 20
        local_results = self.sample_songs[:1]  # Solo 1 resultado local

        self.mock_repository.search.return_value = local_results

        # Act
        result = await self.song_use_cases.search_songs(
            query=query, limit=limit, include_youtube=False
        )

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result, local_results)
        # No debe buscar en YouTube
        self.song_use_cases.music_service.search_and_process_music.assert_not_called()

    async def test_search_songs_existing_youtube_result(self):
        """Test cuando resultado de YouTube ya existe en BD"""
        # Arrange
        query = "existing song"
        limit = 10
        local_results = []
        youtube_tracks = [self.mock_track_data]
        existing_song = self.sample_songs[0]

        self.mock_repository.search.return_value = local_results
        self.song_use_cases.music_service.search_and_process_music.return_value = (
            youtube_tracks
        )
        self.mock_repository.get_by_source.return_value = existing_song  # Ya existe

        # Act
        result = await self.song_use_cases.search_songs(query=query, limit=limit)

        # Assert
        self.mock_repository.get_by_source.assert_called_with(
            "youtube", "youtube-search-123"
        )
        # La canción existente no se debe agregar a los resultados locales
        # porque ya debería estar en los resultados de búsqueda local
        self.assertEqual(len(result), 0)  # Solo resultados locales originales

    async def test_search_songs_empty_query(self):
        """Test búsqueda con query vacío"""
        # Arrange
        query = ""
        limit = 10

        self.mock_repository.search.return_value = []

        # Act
        result = await self.song_use_cases.search_songs(query=query, limit=limit)

        # Assert
        self.assertEqual(len(result), 0)
        self.mock_repository.search.assert_called_once_with(query, limit)

    async def test_search_songs_limit_zero(self):
        """Test búsqueda con límite 0"""
        # Arrange
        query = "test"
        limit = 0

        self.mock_repository.search.return_value = []

        # Act
        result = await self.song_use_cases.search_songs(query=query, limit=limit)

        # Assert
        self.assertEqual(len(result), 0)
        self.mock_repository.search.assert_called_once_with(query, limit)

    async def test_search_songs_default_parameters(self):
        """Test búsqueda con parámetros por defecto"""
        # Arrange
        query = "default test"
        expected_limit = 20  # Default
        expected_include_youtube = True  # Default

        self.mock_repository.search.return_value = self.sample_songs

        # Act
        result = await self.song_use_cases.search_songs(query)

        # Assert
        self.mock_repository.search.assert_called_once_with(query, expected_limit)
        self.assertEqual(len(result), len(self.sample_songs))

    async def test_search_songs_error_handling(self):
        """Test manejo de errores en búsqueda"""
        # Arrange
        query = "error test"
        limit = 10
        local_results = self.sample_songs[:2]

        self.mock_repository.search.return_value = local_results
        # Simular error en YouTube search
        self.song_use_cases.music_service.search_and_process_music.side_effect = (
            Exception("YouTube API Error")
        )

        # Act
        result = await self.song_use_cases.search_songs(query=query, limit=limit)

        # Assert
        # Debe retornar al menos los resultados locales
        self.assertEqual(len(result), len(local_results))
        self.assertEqual(result, local_results)

    async def test_search_songs_case_insensitive(self):
        """Test que la búsqueda funciona con diferentes casos"""
        # Arrange
        test_cases = ["Rock", "ROCK", "rock", "RoCk"]

        for query in test_cases:
            with self.subTest(query=query):
                self.mock_repository.search.return_value = self.sample_songs[:2]

                # Act
                result = await self.song_use_cases.search_songs(query=query)

                # Assert
                self.mock_repository.search.assert_called_with(query, 20)
                self.assertEqual(len(result), 2)

    async def test_search_songs_special_characters(self):
        """Test búsqueda con caracteres especiales"""
        # Arrange
        special_queries = [
            "rock & roll",
            "música clásica",
            "hip-hop/rap",
            "rock'n'roll",
        ]

        for query in special_queries:
            with self.subTest(query=query):
                self.mock_repository.search.return_value = []

                # Act
                result = await self.song_use_cases.search_songs(query=query)

                # Assert
                self.mock_repository.search.assert_called_with(query, 20)


if __name__ == "__main__":
    unittest.main()
