"""
Tests for Song DTOs and API layer components
"""
import pytest
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class MockSongGenre(Enum):
    """Mock song genre enumeration"""
    POP = "pop"
    ROCK = "rock"
    JAZZ = "jazz"
    CLASSICAL = "classical"
    HIP_HOP = "hip_hop"
    ELECTRONIC = "electronic"


class MockSongStatus(Enum):
    """Mock song status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROCESSING = "processing"
    ERROR = "error"


@dataclass
class MockSongCreateDTO:
    """Mock DTO for creating songs"""
    title: str
    artist_name: str
    album_name: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    genre: Optional[MockSongGenre] = None
    youtube_url: Optional[str] = None
    spotify_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate the DTO after initialization"""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Song title is required")
        if not self.artist_name or len(self.artist_name.strip()) == 0:
            raise ValueError("Artist name is required")
        if self.title and len(self.title) > 300:
            raise ValueError("Song title too long")
        if self.duration is not None and self.duration <= 0:
            raise ValueError("Duration must be positive")
        if self.duration is not None and self.duration > 7200:  # 2 hours max
            raise ValueError("Duration too long")


@dataclass
class MockSongResponseDTO:
    """Mock DTO for song responses"""
    id: int
    title: str
    artist_name: str
    album_name: Optional[str] = None
    duration: Optional[int] = None
    genre: Optional[MockSongGenre] = None
    play_count: int = 0
    status: MockSongStatus = MockSongStatus.ACTIVE
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "title": self.title,
            "artist_name": self.artist_name,
            "album_name": self.album_name,
            "duration": self.duration,
            "genre": self.genre.value if self.genre else None,
            "play_count": self.play_count,
            "status": self.status.value,
            "file_url": self.file_url,
            "thumbnail_url": self.thumbnail_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def get_duration_formatted(self) -> str:
        """Get formatted duration string"""
        if not self.duration:
            return "0:00"
        
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"


@dataclass
class MockSongSearchDTO:
    """Mock DTO for song search queries"""
    query: str
    genre: Optional[MockSongGenre] = None
    artist_name: Optional[str] = None
    album_name: Optional[str] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    page: int = 1
    page_size: int = 20
    
    def __post_init__(self):
        """Validate search parameters"""
        if not self.query or len(self.query.strip()) == 0:
            raise ValueError("Search query is required")
        if self.page <= 0:
            raise ValueError("Page must be positive")
        if self.page_size <= 0 or self.page_size > 100:
            raise ValueError("Page size must be between 1 and 100")


@dataclass
class MockPlaylistSongDTO:
    """Mock DTO for songs in playlists"""
    song_id: int
    title: str
    artist_name: str
    duration: Optional[int] = None
    position: int = 0
    added_at: Optional[datetime] = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "song_id": self.song_id,
            "title": self.title,
            "artist_name": self.artist_name,
            "duration": self.duration,
            "position": self.position,
            "added_at": self.added_at.isoformat() if self.added_at else None
        }


class MockSongMapper:
    """Mock mapper for song entities and DTOs"""
    
    @staticmethod
    def create_dto_to_entity(dto: MockSongCreateDTO) -> Dict[str, Any]:
        """Convert create DTO to entity data"""
        return {
            "title": dto.title,
            "artist_name": dto.artist_name,
            "album_name": dto.album_name,
            "duration": dto.duration,
            "genre": dto.genre.value if dto.genre else None,
            "youtube_url": dto.youtube_url,
            "spotify_id": dto.spotify_id,
            "status": MockSongStatus.PROCESSING.value
        }
    
    @staticmethod
    def entity_to_response_dto(entity_data: Dict[str, Any]) -> MockSongResponseDTO:
        """Convert entity data to response DTO"""
        genre = None
        if entity_data.get("genre"):
            try:
                genre = MockSongGenre(entity_data["genre"])
            except ValueError:
                genre = None
        
        status = MockSongStatus.ACTIVE
        if entity_data.get("status"):
            try:
                status = MockSongStatus(entity_data["status"])
            except ValueError:
                status = MockSongStatus.ACTIVE
        
        return MockSongResponseDTO(
            id=entity_data.get("id", 0),
            title=entity_data.get("title", ""),
            artist_name=entity_data.get("artist_name", ""),
            album_name=entity_data.get("album_name"),
            duration=entity_data.get("duration"),
            genre=genre,
            play_count=entity_data.get("play_count", 0),
            status=status,
            file_url=entity_data.get("file_url"),
            thumbnail_url=entity_data.get("thumbnail_url"),
            created_at=entity_data.get("created_at", datetime.now())
        )


class TestSongCreateDTO:
    """Test song creation DTO"""
    
    def test_valid_song_creation(self):
        """Test creating valid song DTO"""
        dto = MockSongCreateDTO(
            title="Test Song",
            artist_name="Test Artist",
            album_name="Test Album",
            duration=180,
            genre=MockSongGenre.POP
        )
        assert dto.title == "Test Song"
        assert dto.artist_name == "Test Artist"
        assert dto.album_name == "Test Album"
        assert dto.duration == 180
        assert dto.genre == MockSongGenre.POP
    
    def test_minimal_song_creation(self):
        """Test creating song with minimal data"""
        dto = MockSongCreateDTO(
            title="Minimal Song",
            artist_name="Minimal Artist"
        )
        assert dto.title == "Minimal Song"
        assert dto.artist_name == "Minimal Artist"
        assert dto.album_name is None
        assert dto.duration is None
        assert dto.genre is None
    
    def test_empty_title_validation(self):
        """Test validation with empty title"""
        with pytest.raises(ValueError, match="Song title is required"):
            MockSongCreateDTO(title="", artist_name="Artist")
    
    def test_empty_artist_validation(self):
        """Test validation with empty artist name"""
        with pytest.raises(ValueError, match="Artist name is required"):
            MockSongCreateDTO(title="Song", artist_name="")
    
    def test_long_title_validation(self):
        """Test validation with too long title"""
        long_title = "A" * 301
        with pytest.raises(ValueError, match="Song title too long"):
            MockSongCreateDTO(title=long_title, artist_name="Artist")
    
    def test_negative_duration_validation(self):
        """Test validation with negative duration"""
        with pytest.raises(ValueError, match="Duration must be positive"):
            MockSongCreateDTO(title="Song", artist_name="Artist", duration=-10)
    
    def test_too_long_duration_validation(self):
        """Test validation with too long duration"""
        with pytest.raises(ValueError, match="Duration too long"):
            MockSongCreateDTO(title="Song", artist_name="Artist", duration=7300)


class TestSongResponseDTO:
    """Test song response DTO"""
    
    def test_response_dto_creation(self):
        """Test creating response DTO"""
        dto = MockSongResponseDTO(
            id=1,
            title="Response Song",
            artist_name="Response Artist",
            duration=240,
            genre=MockSongGenre.ROCK,
            play_count=100
        )
        assert dto.id == 1
        assert dto.title == "Response Song"
        assert dto.artist_name == "Response Artist"
        assert dto.duration == 240
        assert dto.genre == MockSongGenre.ROCK
        assert dto.play_count == 100
        assert dto.status == MockSongStatus.ACTIVE
    
    def test_to_dict_conversion(self):
        """Test converting DTO to dictionary"""
        dto = MockSongResponseDTO(
            id=1,
            title="Dict Song",
            artist_name="Dict Artist",
            genre=MockSongGenre.JAZZ,
            status=MockSongStatus.PROCESSING
        )
        result = dto.to_dict()
        
        assert result["id"] == 1
        assert result["title"] == "Dict Song"
        assert result["artist_name"] == "Dict Artist"
        assert result["genre"] == "jazz"
        assert result["status"] == "processing"
        assert result["play_count"] == 0
        assert "created_at" in result
    
    def test_duration_formatting(self):
        """Test duration formatting"""
        # Test normal duration
        dto = MockSongResponseDTO(id=1, title="Song", artist_name="Artist", duration=185)
        assert dto.get_duration_formatted() == "3:05"
        
        # Test zero duration
        dto.duration = 0
        assert dto.get_duration_formatted() == "0:00"
        
        # Test None duration
        dto.duration = None
        assert dto.get_duration_formatted() == "0:00"
        
        # Test exact minute
        dto.duration = 120
        assert dto.get_duration_formatted() == "2:00"


class TestSongSearchDTO:
    """Test song search DTO"""
    
    def test_valid_search_creation(self):
        """Test creating valid search DTO"""
        dto = MockSongSearchDTO(
            query="test song",
            genre=MockSongGenre.POP,
            artist_name="test artist",
            page=2,
            page_size=10
        )
        assert dto.query == "test song"
        assert dto.genre == MockSongGenre.POP
        assert dto.artist_name == "test artist"
        assert dto.page == 2
        assert dto.page_size == 10
    
    def test_minimal_search_creation(self):
        """Test creating search with minimal data"""
        dto = MockSongSearchDTO(query="minimal")
        assert dto.query == "minimal"
        assert dto.genre is None
        assert dto.page == 1
        assert dto.page_size == 20
    
    def test_empty_query_validation(self):
        """Test validation with empty query"""
        with pytest.raises(ValueError, match="Search query is required"):
            MockSongSearchDTO(query="")
    
    def test_invalid_page_validation(self):
        """Test validation with invalid page"""
        with pytest.raises(ValueError, match="Page must be positive"):
            MockSongSearchDTO(query="test", page=0)
    
    def test_invalid_page_size_validation(self):
        """Test validation with invalid page size"""
        with pytest.raises(ValueError, match="Page size must be between 1 and 100"):
            MockSongSearchDTO(query="test", page_size=0)
        
        with pytest.raises(ValueError, match="Page size must be between 1 and 100"):
            MockSongSearchDTO(query="test", page_size=101)


class TestPlaylistSongDTO:
    """Test playlist song DTO"""
    
    def test_playlist_song_creation(self):
        """Test creating playlist song DTO"""
        dto = MockPlaylistSongDTO(
            song_id=1,
            title="Playlist Song",
            artist_name="Playlist Artist",
            duration=200,
            position=3
        )
        assert dto.song_id == 1
        assert dto.title == "Playlist Song"
        assert dto.artist_name == "Playlist Artist"
        assert dto.duration == 200
        assert dto.position == 3
        assert dto.added_at is not None
    
    def test_playlist_song_to_dict(self):
        """Test converting playlist song to dictionary"""
        dto = MockPlaylistSongDTO(
            song_id=1,
            title="Dict Song",
            artist_name="Dict Artist",
            position=1
        )
        result = dto.to_dict()
        
        assert result["song_id"] == 1
        assert result["title"] == "Dict Song"
        assert result["artist_name"] == "Dict Artist"
        assert result["position"] == 1
        assert "added_at" in result


class TestSongMapper:
    """Test song mapper functionality"""
    
    def test_create_dto_to_entity_mapping(self):
        """Test mapping create DTO to entity"""
        dto = MockSongCreateDTO(
            title="Mapper Song",
            artist_name="Mapper Artist",
            album_name="Mapper Album",
            duration=300,
            genre=MockSongGenre.ELECTRONIC
        )
        
        entity_data = MockSongMapper.create_dto_to_entity(dto)
        
        assert entity_data["title"] == "Mapper Song"
        assert entity_data["artist_name"] == "Mapper Artist"
        assert entity_data["album_name"] == "Mapper Album"
        assert entity_data["duration"] == 300
        assert entity_data["genre"] == "electronic"
        assert entity_data["status"] == "processing"
    
    def test_entity_to_response_dto_mapping(self):
        """Test mapping entity to response DTO"""
        entity_data = {
            "id": 1,
            "title": "Entity Song",
            "artist_name": "Entity Artist",
            "duration": 250,
            "genre": "rock",
            "play_count": 50,
            "status": "active",
            "created_at": datetime(2024, 1, 1)
        }
        
        dto = MockSongMapper.entity_to_response_dto(entity_data)
        
        assert dto.id == 1
        assert dto.title == "Entity Song"
        assert dto.artist_name == "Entity Artist"
        assert dto.duration == 250
        assert dto.genre == MockSongGenre.ROCK
        assert dto.play_count == 50
        assert dto.status == MockSongStatus.ACTIVE
        assert dto.created_at == datetime(2024, 1, 1)
    
    def test_entity_mapping_with_invalid_genre(self):
        """Test entity mapping with invalid genre"""
        entity_data = {
            "id": 1,
            "title": "Invalid Genre Song",
            "artist_name": "Artist",
            "genre": "invalid_genre"
        }
        
        dto = MockSongMapper.entity_to_response_dto(entity_data)
        
        assert dto.genre is None
    
    def test_entity_mapping_with_defaults(self):
        """Test entity mapping with missing fields"""
        entity_data = {"id": 2, "title": "Minimal Entity", "artist_name": "Artist"}
        
        dto = MockSongMapper.entity_to_response_dto(entity_data)
        
        assert dto.id == 2
        assert dto.title == "Minimal Entity"
        assert dto.artist_name == "Artist"
        assert dto.album_name is None
        assert dto.genre is None
        assert dto.play_count == 0
        assert dto.status == MockSongStatus.ACTIVE


class TestSongIntegration:
    """Integration tests for song DTOs and mappers"""
    
    def test_full_song_workflow(self):
        """Test complete song creation and response workflow"""
        # Create DTO
        create_dto = MockSongCreateDTO(
            title="Workflow Song",
            artist_name="Workflow Artist",
            duration=180,
            genre=MockSongGenre.HIP_HOP
        )
        
        # Map to entity
        entity_data = MockSongMapper.create_dto_to_entity(create_dto)
        entity_data["id"] = 1  # Simulate database ID assignment
        entity_data["play_count"] = 0
        entity_data["status"] = "active"
        
        # Map back to response DTO
        response_dto = MockSongMapper.entity_to_response_dto(entity_data)
        
        # Verify workflow
        assert response_dto.id == 1
        assert response_dto.title == "Workflow Song"
        assert response_dto.artist_name == "Workflow Artist"
        assert response_dto.duration == 180
        assert response_dto.genre == MockSongGenre.HIP_HOP
        assert response_dto.status == MockSongStatus.ACTIVE
    
    def test_search_and_results_workflow(self):
        """Test song search workflow"""
        # Create search DTO
        search_dto = MockSongSearchDTO(
            query="test",
            genre=MockSongGenre.ROCK,
            page=1,
            page_size=5
        )
        
        # Simulate search results
        results = []
        for i in range(3):
            song = MockSongResponseDTO(
                id=i+1,
                title=f"Test Song {i+1}",
                artist_name=f"Artist {i+1}",
                genre=MockSongGenre.ROCK
            )
            results.append(song)
        
        # Verify search and results
        assert search_dto.query == "test"
        assert search_dto.genre == MockSongGenre.ROCK
        assert len(results) == 3
        
        # Verify first result
        first_result = results[0]
        assert first_result.title == "Test Song 1"
        assert first_result.genre == MockSongGenre.ROCK
    
    def test_playlist_integration(self):
        """Test playlist song integration"""
        # Create playlist songs
        playlist_songs = []
        for i in range(3):
            playlist_song = MockPlaylistSongDTO(
                song_id=i+1,
                title=f"Playlist Song {i+1}",
                artist_name=f"Artist {i+1}",
                position=i+1
            )
            playlist_songs.append(playlist_song)
        
        # Verify playlist
        assert len(playlist_songs) == 3
        
        # Test conversion to dict
        for i, song in enumerate(playlist_songs):
            song_dict = song.to_dict()
            assert song_dict["song_id"] == i+1
            assert song_dict["position"] == i+1
            assert "added_at" in song_dict
