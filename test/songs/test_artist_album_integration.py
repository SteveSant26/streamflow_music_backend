"""
Tests para verificar la integración de artistas y álbumes
"""

from unittest.mock import AsyncMock, Mock

import pytest
from django.test import TestCase

from apps.albums.domain.entities import AlbumEntity
from apps.albums.use_cases.save_album_use_case import SaveAlbumUseCase
from apps.artists.domain.entities import ArtistEntity
from apps.artists.use_cases.save_artist_use_case import SaveArtistUseCase
from apps.music_search.domain.interfaces import MusicTrackData
from apps.songs.use_cases.music_track_artist_album_extractor_use_case import (
    MusicTrackArtistAlbumExtractorUseCase,
)


class TestArtistAlbumIntegration(TestCase):
    """Tests de integración para artistas y álbumes"""

    def setUp(self):
        self.mock_artist_repo = Mock()
        self.mock_album_repo = Mock()

        # Mock repositories para retornar None (no encontrados)
        self.mock_artist_repo.get_by_source = AsyncMock(return_value=None)
        self.mock_artist_repo.find_by_name = AsyncMock(return_value=None)
        self.mock_album_repo.get_by_source = AsyncMock(return_value=None)

        # Mock save methods
        self.mock_artist_repo.save = AsyncMock()
        self.mock_album_repo.save = AsyncMock()

    async def test_save_artist_use_case_creates_new_artist(self):
        """Test que SaveArtistUseCase crea un nuevo artista correctamente"""

        # Setup
        artist_data = {
            "name": "Test Artist - Topic",
            "source_type": "youtube",
            "source_id": "UC123456789",
            "image_url": "https://example.com/image.jpg",
        }

        expected_artist = ArtistEntity(
            id="test-id",
            name="Test Artist",  # Debe limpiar el " - Topic"
            source_type="youtube",
            source_id="UC123456789",
            image_url="https://example.com/image.jpg",
        )

        self.mock_artist_repo.save.return_value = expected_artist

        use_case = SaveArtistUseCase(self.mock_artist_repo)

        # Execute
        result = await use_case.execute(artist_data)

        # Assert
        assert result is not None
        assert result.name == "Test Artist"
        assert result.source_type == "youtube"
        assert result.source_id == "UC123456789"
        self.mock_artist_repo.save.assert_called_once()

    async def test_save_album_use_case_creates_new_album(self):
        """Test que SaveAlbumUseCase crea un nuevo álbum correctamente"""

        # Setup
        album_data = {
            "title": "Test Album - Single",
            "artist_id": "artist-123",
            "artist_name": "Test Artist",
            "source_type": "youtube",
            "source_id": "album-123",
        }

        expected_album = AlbumEntity(
            id="album-id",
            title="Test Album - Single",
            artist_id="artist-123",
            artist_name="Test Artist",
            source_type="youtube",
            source_id="album-123",
        )

        self.mock_album_repo.save.return_value = expected_album
        self.mock_album_repo.find_or_create_by_title_and_artist = AsyncMock(
            return_value=expected_album
        )

        use_case = SaveAlbumUseCase(self.mock_album_repo)

        # Execute
        result = await use_case.execute(album_data)

        # Assert
        assert result is not None
        assert result.title == "Test Album - Single"
        assert result.artist_id == "artist-123"
        assert result.source_type == "youtube"

    async def test_extractor_processes_track_correctly(self):
        """Test que el extractor procesa un track completo correctamente"""

        # Setup
        track = MusicTrackData(
            video_id="test123",
            title="Test Song",
            artist_name="Test Artist - Topic",
            album_title="Test Album",
            duration_seconds=180,
            thumbnail_url="https://example.com/thumb.jpg",
            genre="Pop",
            tags=["music", "artist", "UC123456789"],
            url="https://youtube.com/watch?v=test123",
        )

        # Mock save use cases
        mock_save_artist = AsyncMock()
        mock_save_album = AsyncMock()

        expected_artist = ArtistEntity(
            id="artist-123",
            name="Test Artist",
            source_type="youtube",
            source_id="UC123456789",
        )

        expected_album = AlbumEntity(
            id="album-123",
            title="Test Album",
            artist_id="artist-123",
            artist_name="Test Artist",
        )

        mock_save_artist.execute.return_value = expected_artist
        mock_save_album.execute.return_value = expected_album

        extractor = MusicTrackArtistAlbumExtractorUseCase(
            self.mock_artist_repo, self.mock_album_repo
        )

        # Override the save use cases
        extractor.save_artist_use_case = mock_save_artist
        extractor.save_album_use_case = mock_save_album

        # Execute
        result = await extractor.execute(track)

        # Assert
        assert result["artist_id"] == "artist-123"
        assert result["album_id"] == "album-123"
        assert result["artist_name"] == "Test Artist"
        assert result["album_title"] == "Test Album"

    def test_clean_artist_name(self):
        """Test de limpieza de nombres de artistas"""

        extractor = MusicTrackArtistAlbumExtractorUseCase(
            self.mock_artist_repo, self.mock_album_repo
        )

        test_cases = [
            ("Artist Name - Topic", "Artist Name"),
            ("Artist VEVO", "Artist"),
            ("Artist Official", "Artist"),
            ("Artist Records", "Artist"),
            ("Artist Music", "Artist"),
            ("Normal Artist", "Normal Artist"),
            ("  Spaced Artist  ", "Spaced Artist"),
        ]

        for input_name, expected in test_cases:
            result = extractor._clean_artist_name(input_name)
            assert result == expected, f"Failed for input: {input_name}"

    def test_clean_album_title(self):
        """Test de limpieza de títulos de álbumes"""

        extractor = MusicTrackArtistAlbumExtractorUseCase(
            self.mock_artist_repo, self.mock_album_repo
        )

        test_cases = [
            ("Album Title - Single", "Song Title", "Album Title"),
            ("Song Title", "Song Title", "Song Title - Single"),
            ("Album Title - EP", "Song Title", "Album Title"),
            ("Album Title - Album", "Song Title", "Album Title"),
            ("Normal Album", "Song Title", "Normal Album"),
        ]

        for album_input, song_title, expected in test_cases:
            result = extractor._clean_album_title(album_input, song_title)
            assert result == expected, f"Failed for input: {album_input}, {song_title}"


# Ejemplo de test de integración real (requiere configuración de Django)
class TestDatabaseIntegration(TestCase):
    """Tests de integración con base de datos real"""

    @pytest.mark.django_db
    async def test_full_integration_flow(self):
        """Test del flujo completo con base de datos"""

        # Este test requeriría configuración completa de Django y BD
        # y se ejecutaría con datos reales

        from apps.albums.infrastructure.repository.album_repository import (
            AlbumRepository,
        )
        from apps.artists.infrastructure.repository.artist_repository import (
            ArtistRepository,
        )

        artist_repo = ArtistRepository()
        album_repo = AlbumRepository()

        # Crear un track de ejemplo
        track = MusicTrackData(
            video_id="integration_test",
            title="Integration Test Song",
            artist_name="Integration Artist",
            album_title="Integration Album",
            duration_seconds=200,
            thumbnail_url="https://example.com/test.jpg",
            genre="Test",
            tags=["test"],
            url="https://youtube.com/test",
        )

        # Ejecutar el extractor
        extractor = MusicTrackArtistAlbumExtractorUseCase(artist_repo, album_repo)
        result = await extractor.execute(track)

        # Verificar que se crearon las entidades
        assert result["artist_id"] is not None
        assert result["artist_name"] == "Integration Artist"

        # Verificar en base de datos
        saved_artist = await artist_repo.get(result["artist_id"])
        assert saved_artist is not None
        assert saved_artist.name == "Integration Artist"


if __name__ == "__main__":
    pytest.main([__file__])
