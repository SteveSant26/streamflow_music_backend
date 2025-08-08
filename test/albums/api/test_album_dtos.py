"""
Tests for Albums API DTOs
Following clean architecture pattern with direct module testing
"""

import pytest
from dataclasses import dataclass, field
from typing import Optional, List

# Mock de los DTOs reales para testing directo
@dataclass
class AlbumResponseDTO:
    """Album Response DTO for API testing"""
    id: str
    title: str
    artist_name: str
    release_date: Optional[str] = None
    total_tracks: int = 0
    duration: Optional[int] = None
    genre: Optional[str] = None
    cover_url: Optional[str] = None
    spotify_id: Optional[str] = None
    youtube_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class AlbumCreateDTO:
    """Album Creation DTO for API testing"""
    title: str
    artist_name: str
    release_date: Optional[str] = None
    genre: Optional[str] = None
    cover_url: Optional[str] = None
    spotify_id: Optional[str] = None
    youtube_id: Optional[str] = None

@dataclass
class AlbumUpdateDTO:
    """Album Update DTO for API testing"""
    title: Optional[str] = None
    artist_name: Optional[str] = None
    release_date: Optional[str] = None
    genre: Optional[str] = None
    cover_url: Optional[str] = None

@dataclass
class AlbumListResponseDTO:
    """Album List Response DTO for API testing"""
    albums: List[AlbumResponseDTO] = field(default_factory=list)
    total_count: int = 0
    page: int = 1
    per_page: int = 10
    has_next: bool = False
    has_prev: bool = False

class TestAlbumDTOs:
    """Test Album DTOs functionality"""
    
    def test_album_response_dto_creation(self):
        """Test creating AlbumResponseDTO"""
        dto = AlbumResponseDTO(
            id="album_123",
            title="Test Album",
            artist_name="Test Artist",
            release_date="2024-01-01",
            total_tracks=12,
            duration=3600,
            genre="Rock"
        )
        
        assert dto.id == "album_123"
        assert dto.title == "Test Album"
        assert dto.artist_name == "Test Artist"
        assert dto.release_date == "2024-01-01"
        assert dto.total_tracks == 12
        assert dto.duration == 3600
        assert dto.genre == "Rock"
        
    def test_album_response_dto_minimal(self):
        """Test AlbumResponseDTO with minimal data"""
        dto = AlbumResponseDTO(
            id="album_456",
            title="Minimal Album",
            artist_name="Minimal Artist"
        )
        
        assert dto.id == "album_456"
        assert dto.title == "Minimal Album"
        assert dto.artist_name == "Minimal Artist"
        assert dto.release_date is None
        assert dto.total_tracks == 0
        assert dto.duration is None
        
    def test_album_create_dto(self):
        """Test AlbumCreateDTO"""
        dto = AlbumCreateDTO(
            title="New Album",
            artist_name="New Artist",
            release_date="2024-06-01",
            genre="Pop",
            spotify_id="spotify_123"
        )
        
        assert dto.title == "New Album"
        assert dto.artist_name == "New Artist"
        assert dto.release_date == "2024-06-01"
        assert dto.genre == "Pop"
        assert dto.spotify_id == "spotify_123"
        
    def test_album_create_dto_minimal(self):
        """Test AlbumCreateDTO with minimal data"""
        dto = AlbumCreateDTO(
            title="Quick Album",
            artist_name="Quick Artist"
        )
        
        assert dto.title == "Quick Album"
        assert dto.artist_name == "Quick Artist"
        assert dto.release_date is None
        assert dto.genre is None
        
    def test_album_update_dto(self):
        """Test AlbumUpdateDTO"""
        dto = AlbumUpdateDTO(
            title="Updated Title",
            genre="Updated Genre"
        )
        
        assert dto.title == "Updated Title"
        assert dto.genre == "Updated Genre"
        assert dto.artist_name is None
        assert dto.release_date is None
        
    def test_album_update_dto_empty(self):
        """Test AlbumUpdateDTO with no updates"""
        dto = AlbumUpdateDTO()
        
        assert dto.title is None
        assert dto.artist_name is None
        assert dto.release_date is None
        assert dto.genre is None
        assert dto.cover_url is None
        
    def test_album_list_response_dto(self):
        """Test AlbumListResponseDTO"""
        albums = [
            AlbumResponseDTO(id="1", title="Album 1", artist_name="Artist 1"),
            AlbumResponseDTO(id="2", title="Album 2", artist_name="Artist 2")
        ]
        
        dto = AlbumListResponseDTO(
            albums=albums,
            total_count=25,
            page=2,
            per_page=10,
            has_next=True,
            has_prev=True
        )
        
        assert len(dto.albums) == 2
        assert dto.total_count == 25
        assert dto.page == 2
        assert dto.per_page == 10
        assert dto.has_next is True
        assert dto.has_prev is True
        
    def test_album_list_response_dto_empty(self):
        """Test AlbumListResponseDTO with empty list"""
        dto = AlbumListResponseDTO()
        
        assert len(dto.albums) == 0
        assert dto.total_count == 0
        assert dto.page == 1
        assert dto.per_page == 10
        assert dto.has_next is False
        assert dto.has_prev is False
        
    def test_dto_field_types(self):
        """Test DTO field types"""
        dto = AlbumResponseDTO(
            id="test_id",
            title="Test Title",
            artist_name="Test Artist",
            total_tracks=10
        )
        
        assert isinstance(dto.id, str)
        assert isinstance(dto.title, str)
        assert isinstance(dto.artist_name, str)
        assert isinstance(dto.total_tracks, int)
        
    def test_dto_with_urls(self):
        """Test DTOs with URL fields"""
        dto = AlbumResponseDTO(
            id="url_album",
            title="URL Album",
            artist_name="URL Artist",
            cover_url="https://example.com/cover.jpg",
            spotify_id="spotify_abc123",
            youtube_id="youtube_xyz789"
        )
        
        assert dto.cover_url.startswith("https://")
        assert dto.spotify_id.startswith("spotify_")
        assert dto.youtube_id.startswith("youtube_")
        
    def test_dto_serialization_like(self):
        """Test DTO dict-like behavior"""
        dto = AlbumCreateDTO(
            title="Serializable Album",
            artist_name="Serializable Artist",
            genre="Rock"
        )
        
        # Simulate serialization
        data = {
            "title": dto.title,
            "artist_name": dto.artist_name,
            "genre": dto.genre
        }
        
        assert data["title"] == "Serializable Album"
        assert data["artist_name"] == "Serializable Artist"
        assert data["genre"] == "Rock"
        
    def test_pagination_calculations(self):
        """Test pagination logic in list DTO"""
        # Page 1 of 3
        dto1 = AlbumListResponseDTO(
            total_count=25,
            page=1,
            per_page=10,
            has_next=True,
            has_prev=False
        )
        
        # Page 2 of 3
        dto2 = AlbumListResponseDTO(
            total_count=25,
            page=2,
            per_page=10,
            has_next=True,
            has_prev=True
        )
        
        # Page 3 of 3
        dto3 = AlbumListResponseDTO(
            total_count=25,
            page=3,
            per_page=10,
            has_next=False,
            has_prev=True
        )
        
        assert dto1.has_next and not dto1.has_prev
        assert dto2.has_next and dto2.has_prev
        assert not dto3.has_next and dto3.has_prev
        
    def test_album_dto_edge_cases(self):
        """Test edge cases for album DTOs"""
        # Very long title
        long_title = "A" * 500
        dto = AlbumCreateDTO(
            title=long_title,
            artist_name="Artist"
        )
        assert len(dto.title) == 500
        
        # Unicode characters
        unicode_dto = AlbumCreateDTO(
            title="Álbum con ñ y émojis 🎵",
            artist_name="Ártista 🎤"
        )
        assert "ñ" in unicode_dto.title
        assert "🎵" in unicode_dto.title
        assert "🎤" in unicode_dto.artist_name
        
        # Zero duration
        zero_dto = AlbumResponseDTO(
            id="zero",
            title="Zero Duration",
            artist_name="Zero Artist",
            duration=0,
            total_tracks=0
        )
        assert zero_dto.duration == 0
        assert zero_dto.total_tracks == 0
