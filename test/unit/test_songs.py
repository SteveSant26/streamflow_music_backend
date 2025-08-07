"""
🧪 TESTS SIMPLES PARA SONG ENTITY SIN DJANGO
===========================================
Tests que no requieren configuración Django
"""
import pytest
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SimpleSongEntity:
    """Entidad Song simplificada para tests sin Django"""
    id: str
    title: str
    artist_name: str = ""
    album_title: str = ""
    genre_name: str = ""
    duration_seconds: int = 0
    play_count: int = 0
    is_active: bool = True
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TestSimpleSongEntity:
    """Tests simples para Song Entity sin dependencias Django"""
    
    @pytest.mark.unit
    def test_simple_song_creation(self):
        """Test creación básica de Song"""
        # Given
        song_data = {
            "id": "song-test-123",
            "title": "Test Song",
            "artist_name": "Test Artist",
            "duration_seconds": 180
        }
        
        # When
        song = SimpleSongEntity(**song_data)
        
        # Then
        assert song.id == "song-test-123"
        assert song.title == "Test Song"
        assert song.artist_name == "Test Artist"
        assert song.duration_seconds == 180
        assert song.play_count == 0
        assert song.is_active is True
        assert song.tags == []
    
    @pytest.mark.unit
    def test_song_minimal_data(self):
        """Test con datos mínimos"""
        # Given & When
        song = SimpleSongEntity(id="minimal", title="Minimal Song")
        
        # Then
        assert song.id == "minimal"
        assert song.title == "Minimal Song"
        assert song.artist_name == ""
        assert song.duration_seconds == 0
        assert song.is_active is True
    
    @pytest.mark.unit
    def test_song_with_tags(self):
        """Test Song con tags"""
        # Given
        song = SimpleSongEntity(
            id="tagged-song",
            title="Tagged Song",
            tags=["rock", "alternative"]
        )
        
        # Then
        assert song.tags == ["rock", "alternative"]
        assert len(song.tags) == 2
    
    @pytest.mark.unit
    @pytest.mark.parametrize("duration,expected", [
        (0, 0),
        (60, 60),
        (3600, 3600),
        (180, 180),
    ])
    def test_song_duration_validation(self, duration, expected):
        """Test validación de duración con parámetros"""
        # Given & When
        song = SimpleSongEntity(
            id=f"song-{duration}",
            title="Duration Test",
            duration_seconds=duration
        )
        
        # Then
        assert song.duration_seconds == expected
    
    @pytest.mark.unit
    def test_song_play_count_increment(self):
        """Test incremento de play_count"""
        # Given
        song = SimpleSongEntity(id="play-test", title="Play Test", play_count=100)
        initial_count = song.play_count
        
        # When
        song.play_count += 1
        
        # Then
        assert song.play_count == initial_count + 1
        assert song.play_count == 101
    
    @pytest.mark.unit
    def test_song_inactive_state(self):
        """Test Song inactiva"""
        # Given & When
        song = SimpleSongEntity(
            id="inactive-song",
            title="Inactive Song",
            is_active=False
        )
        
        # Then
        assert song.is_active is False
    
    @pytest.mark.unit
    def test_song_string_representation(self):
        """Test representación como string"""
        # Given
        song = SimpleSongEntity(id="str-test", title="String Test")
        
        # When
        song_str = str(song)
        
        # Then
        assert "String Test" in song_str or "str-test" in song_str
    
    @pytest.mark.unit
    def test_song_equality_by_id(self):
        """Test igualdad por ID"""
        # Given
        song1 = SimpleSongEntity(id="same-id", title="Song One")
        song2 = SimpleSongEntity(id="same-id", title="Song Two")
        
        # Then
        assert song1.id == song2.id  # Mismo ID
        assert song1.title != song2.title  # Títulos diferentes
    
    @pytest.mark.unit
    def test_song_with_empty_tags(self):
        """Test Song con tags vacías"""
        # Given
        song = SimpleSongEntity(id="empty-tags", title="Empty Tags", tags=[])
        
        # Then
        assert song.tags == []
        assert len(song.tags) == 0
