"""
🧪 TESTS SIMPLES PARA ALBUM ENTITY
=================================
Tests unitarios para Album sin dependencias Django
"""
import pytest
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SimpleAlbumEntity:
    """Entidad Album simplificada para tests"""
    id: str
    title: str
    artist_name: str = ""
    release_date: str = ""
    total_tracks: int = 0
    duration_seconds: int = 0
    genre_name: str = ""
    is_active: bool = True
    cover_image_url: str = ""


class TestSimpleAlbumEntity:
    """Tests simples para Album Entity"""
    
    @pytest.mark.unit
    def test_album_creation_complete(self):
        """Test creación completa de Album"""
        # Given
        album_data = {
            "id": "album-123",
            "title": "Test Album",
            "artist_name": "Test Artist",
            "release_date": "2024-01-01",
            "total_tracks": 12,
            "duration_seconds": 2400,
            "genre_name": "Rock"
        }
        
        # When
        album = SimpleAlbumEntity(**album_data)
        
        # Then
        assert album.id == "album-123"
        assert album.title == "Test Album"
        assert album.artist_name == "Test Artist"
        assert album.release_date == "2024-01-01"
        assert album.total_tracks == 12
        assert album.duration_seconds == 2400
        assert album.genre_name == "Rock"
        assert album.is_active is True
    
    @pytest.mark.unit
    def test_album_minimal_creation(self):
        """Test creación mínima de Album"""
        # Given & When
        album = SimpleAlbumEntity(id="minimal", title="Minimal Album")
        
        # Then
        assert album.id == "minimal"
        assert album.title == "Minimal Album"
        assert album.artist_name == ""
        assert album.total_tracks == 0
        assert album.is_active is True
    
    @pytest.mark.unit
    @pytest.mark.parametrize("tracks,album_type", [
        (1, "Single"),
        (3, "EP"), 
        (6, "EP"),
        (8, "Album"),
        (12, "Album"),
        (20, "Album"),
    ])
    def test_album_type_by_tracks(self, tracks, album_type):
        """Test tipo de álbum por número de tracks"""
        # Given
        album = SimpleAlbumEntity(
            id=f"album-{tracks}",
            title="Test Album",
            total_tracks=tracks
        )
        
        # When
        if album.total_tracks == 1:
            calculated_type = "Single"
        elif album.total_tracks <= 6:
            calculated_type = "EP"
        else:
            calculated_type = "Album"
        
        # Then
        assert calculated_type == album_type
    
    @pytest.mark.unit
    def test_album_duration_calculation(self):
        """Test cálculo de duración promedio por track"""
        # Given
        album = SimpleAlbumEntity(
            id="duration-test",
            title="Duration Test",
            total_tracks=10,
            duration_seconds=3000  # 50 minutos
        )
        
        # When
        avg_track_duration = album.duration_seconds / album.total_tracks if album.total_tracks > 0 else 0
        
        # Then
        assert avg_track_duration == 300  # 5 minutos por track
    
    @pytest.mark.unit
    def test_album_with_cover_image(self):
        """Test Album con imagen de portada"""
        # Given
        cover_url = "https://example.com/album-cover.jpg"
        album = SimpleAlbumEntity(
            id="with-cover",
            title="Album with Cover",
            cover_image_url=cover_url
        )
        
        # Then
        assert album.cover_image_url == cover_url
        assert "https://" in album.cover_image_url
    
    @pytest.mark.unit
    def test_album_inactive_state(self):
        """Test Album inactivo"""
        # Given & When
        album = SimpleAlbumEntity(
            id="inactive",
            title="Inactive Album",
            is_active=False
        )
        
        # Then
        assert album.is_active is False
    
    @pytest.mark.unit
    def test_album_release_year_extraction(self):
        """Test extracción del año de lanzamiento"""
        # Given
        album = SimpleAlbumEntity(
            id="year-test",
            title="Year Test",
            release_date="2024-03-15"
        )
        
        # When
        release_year = album.release_date.split("-")[0] if album.release_date else ""
        
        # Then
        assert release_year == "2024"
    
    @pytest.mark.unit
    @pytest.mark.parametrize("genre", [
        "Rock",
        "Pop", 
        "Electronic",
        "Hip-Hop",
        "Classical",
        "Jazz"
    ])
    def test_album_different_genres(self, genre):
        """Test Album con diferentes géneros"""
        # Given & When
        album = SimpleAlbumEntity(
            id=f"genre-{genre.lower()}",
            title=f"{genre} Album",
            genre_name=genre
        )
        
        # Then
        assert album.genre_name == genre
        assert len(album.genre_name) > 0
    
    @pytest.mark.unit
    def test_album_string_representation(self):
        """Test representación como string"""
        # Given
        album = SimpleAlbumEntity(
            id="str-test",
            title="String Test Album",
            artist_name="Test Artist"
        )
        
        # When
        album_str = str(album)
        
        # Then
        assert "String Test Album" in album_str or "str-test" in album_str
    
    @pytest.mark.unit
    def test_album_equality_by_id(self):
        """Test igualdad por ID"""
        # Given
        album1 = SimpleAlbumEntity(id="same-id", title="Album One")
        album2 = SimpleAlbumEntity(id="same-id", title="Album Two")
        
        # Then
        assert album1.id == album2.id
        assert album1.title != album2.title
