"""
Tests para casos de uso de obtener canciones aleatorias
"""
<<<<<<< HEAD

=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
# Configurar path antes de importar
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from apps.songs.domain.entities import SongEntity
from apps.songs.use_cases.song_use_cases import SongUseCases


class TestGetRandomSongs(unittest.IsolatedAsyncioTestCase):
    """Tests para el caso de uso get_random_songs"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Mock del repositorio
        self.mock_repository = Mock()
        self.mock_repository.get_random = AsyncMock()
        self.mock_repository.get_by_source = AsyncMock()
        self.mock_repository.create = AsyncMock()

        # Instancia del caso de uso
        self.song_use_cases = SongUseCases(self.mock_repository)

        # Mock del music service
        self.song_use_cases.music_service = Mock()
        self.song_use_cases.music_service.get_random_music_tracks = AsyncMock()

        # Datos de prueba
        self.sample_songs = [
            SongEntity(
                id=f"song-{i}",
                title=f"Test Song {i}",
                artist_name=f"Artist {i}",
                album_title=f"Album {i}",
                duration_seconds=180,
                is_active=True,
            )
            for i in range(1, 7)
        ]

        # Mock track data de YouTube
        self.mock_track_data = Mock()
        self.mock_track_data.video_id = "youtube-123"
        self.mock_track_data.title = "YouTube Song"
        self.mock_track_data.artist = "YouTube Artist"
        self.mock_track_data.duration = 200

    async def test_get_random_songs_from_database_sufficient(self):
        """Test obtener canciones aleatorias cuando hay suficientes en BD"""
        # Arrange
        count = 6
        self.mock_repository.get_random.return_value = self.sample_songs[:count]

        # Act
        result = await self.song_use_cases.get_random_songs(count=count)

        # Assert
        self.assertEqual(len(result), count)
        self.mock_repository.get_random.assert_called_once_with(count)
        self.song_use_cases.music_service.get_random_music_tracks.assert_not_called()

    async def test_get_random_songs_from_database_insufficient(self):
        """Test cuando no hay suficientes canciones en BD, busca en YouTube"""
        # Arrange
        count = 6
        existing_songs = self.sample_songs[:3]  # Solo 3 canciones existentes
        new_tracks = [self.mock_track_data]

        self.mock_repository.get_random.side_effect = [
            existing_songs,  # Primera llamada retorna 3 canciones
            [],  # Segunda llamada (para completar) retorna vacío
        ]
        self.song_use_cases.music_service.get_random_music_tracks.return_value = (
            new_tracks
        )
        self.mock_repository.get_by_source.return_value = None  # No existe la canción

        # Mock para _save_track_as_song
        new_song = SongEntity(
            id="new-song",
            title="New YouTube Song",
            artist_name="YouTube Artist",
            source_type="youtube",
            source_id="youtube-123",
        )

        with patch.object(
            self.song_use_cases, "_save_track_as_song", return_value=new_song
        ):
            # Act
            result = await self.song_use_cases.get_random_songs(count=count)

            # Assert
            self.assertGreaterEqual(len(result), 1)  # Al menos debe retornar algo
            self.song_use_cases.music_service.get_random_music_tracks.assert_called_once_with(
                count
            )

    async def test_get_random_songs_force_refresh(self):
        """Test forzar refresh de canciones desde YouTube"""
        # Arrange
        count = 3
        new_tracks = [self.mock_track_data]

        self.song_use_cases.music_service.get_random_music_tracks.return_value = (
            new_tracks
        )
        self.mock_repository.get_by_source.return_value = None

        new_song = SongEntity(
            id="forced-song",
            title="Forced YouTube Song",
            artist_name="YouTube Artist",
            source_type="youtube",
        )

        with patch.object(
            self.song_use_cases, "_save_track_as_song", return_value=new_song
        ):
            # Act
            result = await self.song_use_cases.get_random_songs(
                count=count, force_refresh=True
            )

            # Assert
            self.song_use_cases.music_service.get_random_music_tracks.assert_called_once_with(
                count
            )
            # No debe llamar get_random inicialmente debido a force_refresh
            self.mock_repository.get_random.assert_called()  # Puede llamarse para completar

    async def test_get_random_songs_existing_youtube_song(self):
        """Test cuando la canción de YouTube ya existe en BD"""
        # Arrange
        count = 3
        existing_song = self.sample_songs[0]
        new_tracks = [self.mock_track_data]

        self.mock_repository.get_random.return_value = []  # No hay canciones locales
        self.song_use_cases.music_service.get_random_music_tracks.return_value = (
            new_tracks
        )
        self.mock_repository.get_by_source.return_value = (
            existing_song  # Canción ya existe
        )

        # Act
        result = await self.song_use_cases.get_random_songs(count=count)

        # Assert
        self.assertIn(existing_song, result)
        self.mock_repository.get_by_source.assert_called_with("youtube", "youtube-123")

    async def test_get_random_songs_error_handling(self):
        """Test manejo de errores devuelve canciones existentes"""
        # Arrange
        count = 3
        fallback_songs = self.sample_songs[:count]

        # Simular error en music service
        self.song_use_cases.music_service.get_random_music_tracks.side_effect = (
            Exception("YouTube API Error")
        )
        self.mock_repository.get_random.side_effect = [
            [],  # Primera llamada (normal) vacía
            fallback_songs,  # Segunda llamada (fallback) con canciones
        ]

        # Act
        result = await self.song_use_cases.get_random_songs(count=count)

        # Assert
        self.assertEqual(result, fallback_songs)
        self.assertEqual(len(result), count)

    async def test_get_random_songs_empty_count(self):
        """Test con count = 0"""
        # Act
        result = await self.song_use_cases.get_random_songs(count=0)

        # Assert
        self.assertEqual(len(result), 0)
        self.mock_repository.get_random.assert_called_once_with(0)

    async def test_get_random_songs_default_count(self):
        """Test con count por defecto (6)"""
        # Arrange
        self.mock_repository.get_random.return_value = self.sample_songs

        # Act
        result = await self.song_use_cases.get_random_songs()

        # Assert
        self.mock_repository.get_random.assert_called_once_with(6)  # Default count
        self.assertEqual(len(result), 6)


if __name__ == "__main__":
    unittest.main()
