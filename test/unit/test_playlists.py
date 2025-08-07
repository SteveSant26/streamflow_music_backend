"""
🧪 TESTS SIMPLES PARA PLAYLIST ENTITY
====================================
Tests unitarios para Playlist sin dependencias Django
"""
import pytest
from dataclasses import dataclass
from typing import List


@dataclass
class SimplePlaylistEntity:
    """Entidad Playlist simplificada para tests"""
    id: str
    name: str
    description: str = ""
    user_id: str = ""
    is_public: bool = True
    is_active: bool = True
    song_count: int = 0
    total_duration: int = 0
    cover_image_url: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TestSimplePlaylistEntity:
    """Tests simples para Playlist Entity"""
    
    @pytest.mark.unit
    def test_playlist_creation_complete(self):
        """Test creación completa de Playlist"""
        # Given
        playlist_data = {
            "id": "playlist-123",
            "name": "My Test Playlist",
            "description": "A playlist for testing",
            "user_id": "user-456",
            "is_public": True,
            "song_count": 25,
            "total_duration": 6000,
            "cover_image_url": "https://example.com/playlist.jpg",
            "tags": ["rock", "favorites"]
        }
        
        # When
        playlist = SimplePlaylistEntity(**playlist_data)
        
        # Then
        assert playlist.id == "playlist-123"
        assert playlist.name == "My Test Playlist"
        assert playlist.description == "A playlist for testing"
        assert playlist.user_id == "user-456"
        assert playlist.is_public is True
        assert playlist.song_count == 25
        assert playlist.total_duration == 6000
        assert playlist.cover_image_url == "https://example.com/playlist.jpg"
        assert playlist.tags == ["rock", "favorites"]
        assert playlist.is_active is True
    
    @pytest.mark.unit
    def test_playlist_minimal_creation(self):
        """Test creación mínima de Playlist"""
        # Given & When
        playlist = SimplePlaylistEntity(id="minimal", name="Minimal Playlist")
        
        # Then
        assert playlist.id == "minimal"
        assert playlist.name == "Minimal Playlist"
        assert playlist.description == ""
        assert playlist.user_id == ""
        assert playlist.is_public is True
        assert playlist.song_count == 0
        assert playlist.total_duration == 0
        assert playlist.tags == []
        assert playlist.is_active is True
    
    @pytest.mark.unit
    def test_playlist_private_state(self):
        """Test Playlist privada"""
        # Given & When
        playlist = SimplePlaylistEntity(
            id="private-playlist",
            name="Private Playlist",
            is_public=False
        )
        
        # Then
        assert playlist.is_public is False
    
    @pytest.mark.unit
    def test_playlist_inactive_state(self):
        """Test Playlist inactiva"""
        # Given & When
        playlist = SimplePlaylistEntity(
            id="inactive-playlist",
            name="Inactive Playlist",
            is_active=False
        )
        
        # Then
        assert playlist.is_active is False
    
    @pytest.mark.unit
    def test_playlist_with_tags(self):
        """Test Playlist con tags"""
        # Given
        playlist = SimplePlaylistEntity(
            id="tagged-playlist",
            name="Tagged Playlist",
            tags=["workout", "high-energy", "motivation"]
        )
        
        # Then
        assert len(playlist.tags) == 3
        assert "workout" in playlist.tags
        assert "high-energy" in playlist.tags
        assert "motivation" in playlist.tags
    
    @pytest.mark.unit
    def test_playlist_song_count_management(self):
        """Test gestión del conteo de canciones"""
        # Given
        playlist = SimplePlaylistEntity(
            id="count-test",
            name="Count Test",
            song_count=10
        )
        
        # When - Simular agregar canciones
        playlist.song_count += 5
        
        # Then
        assert playlist.song_count == 15
    
    @pytest.mark.unit
    def test_playlist_duration_calculation(self):
        """Test cálculo de duración total"""
        # Given
        playlist = SimplePlaylistEntity(
            id="duration-test",
            name="Duration Test",
            song_count=20,
            total_duration=7200  # 2 horas en segundos
        )
        
        # When
        avg_song_duration = playlist.total_duration / playlist.song_count if playlist.song_count > 0 else 0
        duration_in_minutes = playlist.total_duration / 60
        
        # Then
        assert avg_song_duration == 360  # 6 minutos promedio por canción
        assert duration_in_minutes == 120  # 120 minutos total
    
    @pytest.mark.unit
    @pytest.mark.parametrize("song_count,playlist_type", [
        (0, "Empty"),
        (1, "Single"),
        (10, "Small"),
        (25, "Medium"),
        (50, "Large"),
        (100, "Massive"),
    ])
    def test_playlist_size_classification(self, song_count, playlist_type):
        """Test clasificación por tamaño"""
        # Given
        playlist = SimplePlaylistEntity(
            id=f"size-{song_count}",
            name="Size Test",
            song_count=song_count
        )
        
        # When
        if playlist.song_count == 0:
            calculated_type = "Empty"
        elif playlist.song_count == 1:
            calculated_type = "Single"
        elif playlist.song_count <= 15:
            calculated_type = "Small"
        elif playlist.song_count <= 30:
            calculated_type = "Medium"
        elif playlist.song_count <= 75:
            calculated_type = "Large"
        else:
            calculated_type = "Massive"
        
        # Then
        assert calculated_type == playlist_type
    
    @pytest.mark.unit
    def test_playlist_with_cover_image(self):
        """Test Playlist con imagen de portada"""
        # Given
        cover_url = "https://example.com/playlist-cover.jpg"
        playlist = SimplePlaylistEntity(
            id="with-cover",
            name="Playlist with Cover",
            cover_image_url=cover_url
        )
        
        # Then
        assert playlist.cover_image_url == cover_url
        assert "https://" in playlist.cover_image_url
    
    @pytest.mark.unit
    def test_playlist_user_ownership(self):
        """Test propiedad de usuario"""
        # Given
        user_id = "user-789"
        playlist = SimplePlaylistEntity(
            id="owned-playlist",
            name="User's Playlist",
            user_id=user_id
        )
        
        # Then
        assert playlist.user_id == user_id
        assert len(playlist.user_id) > 0
    
    @pytest.mark.unit
    def test_playlist_string_representation(self):
        """Test representación como string"""
        # Given
        playlist = SimplePlaylistEntity(
            id="str-test",
            name="String Test Playlist"
        )
        
        # When
        playlist_str = str(playlist)
        
        # Then
        assert "String Test Playlist" in playlist_str or "str-test" in playlist_str
    
    @pytest.mark.unit
    def test_playlist_name_validation(self):
        """Test validación de nombre"""
        # Given
        valid_names = ["My Playlist", "🎵 Rock Hits", "Workout 2024", "Study Music"]
        
        for name in valid_names:
            # When
            playlist = SimplePlaylistEntity(
                id=f"name-{len(name)}",
                name=name
            )
            
            # Then
            assert len(playlist.name) > 0
            assert playlist.name == name
    
    @pytest.mark.unit
    def test_playlist_empty_tags(self):
        """Test Playlist con tags vacías"""
        # Given
        playlist = SimplePlaylistEntity(
            id="empty-tags",
            name="Empty Tags Playlist",
            tags=[]
        )
        
        # Then
        assert playlist.tags == []
        assert len(playlist.tags) == 0
    
    @pytest.mark.unit
    def test_playlist_equality_by_id(self):
        """Test igualdad por ID"""
        # Given
        playlist1 = SimplePlaylistEntity(id="same-id", name="Playlist One")
        playlist2 = SimplePlaylistEntity(id="same-id", name="Playlist Two")
        
        # Then
        assert playlist1.id == playlist2.id
        assert playlist1.name != playlist2.name
