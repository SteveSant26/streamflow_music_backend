"""
Tests for Artist DTOs and API layer components
"""
import pytest
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MockArtistStatus(Enum):
    """Mock artist status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


@dataclass
class MockArtistCreateDTO:
    """Mock DTO for creating artists"""
    name: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
    spotify_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate the DTO after initialization"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Artist name is required")
        if self.name and len(self.name) > 200:
            raise ValueError("Artist name too long")


@dataclass
class MockArtistResponseDTO:
    """Mock DTO for artist responses"""
    id: int
    name: str
    bio: Optional[str] = None
    image_url: Optional[str] = None
    spotify_id: Optional[str] = None
    status: MockArtistStatus = MockArtistStatus.ACTIVE
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio,
            "image_url": self.image_url,
            "spotify_id": self.spotify_id,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class MockArtistListDTO:
    """Mock DTO for artist listings"""
    artists: List[MockArtistResponseDTO] = field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 10
    
    def add_artist(self, artist: MockArtistResponseDTO):
        """Add an artist to the list"""
        self.artists.append(artist)
        self.total_count = len(self.artists)


class MockArtistMapper:
    """Mock mapper for artist entities and DTOs"""
    
    @staticmethod
    def create_dto_to_entity(dto: MockArtistCreateDTO) -> dict:
        """Convert create DTO to entity data"""
        return {
            "name": dto.name,
            "bio": dto.bio,
            "image_url": dto.image_url,
            "spotify_id": dto.spotify_id
        }
    
    @staticmethod
    def entity_to_response_dto(entity_data: dict) -> MockArtistResponseDTO:
        """Convert entity data to response DTO"""
        return MockArtistResponseDTO(
            id=entity_data.get("id", 0),
            name=entity_data.get("name", ""),
            bio=entity_data.get("bio"),
            image_url=entity_data.get("image_url"),
            spotify_id=entity_data.get("spotify_id"),
            status=MockArtistStatus(entity_data.get("status", "active")),
            created_at=entity_data.get("created_at", datetime.now())
        )


class TestArtistCreateDTO:
    """Test artist creation DTO"""
    
    def test_valid_artist_creation(self):
        """Test creating valid artist DTO"""
        dto = MockArtistCreateDTO(
            name="Test Artist",
            bio="Test bio",
            image_url="https://example.com/image.jpg"
        )
        assert dto.name == "Test Artist"
        assert dto.bio == "Test bio"
        assert dto.image_url == "https://example.com/image.jpg"
        assert dto.spotify_id is None
    
    def test_minimal_artist_creation(self):
        """Test creating artist with minimal data"""
        dto = MockArtistCreateDTO(name="Minimal Artist")
        assert dto.name == "Minimal Artist"
        assert dto.bio is None
        assert dto.image_url is None
        assert dto.spotify_id is None
    
    def test_empty_name_validation(self):
        """Test validation with empty name"""
        with pytest.raises(ValueError, match="Artist name is required"):
            MockArtistCreateDTO(name="")
    
    def test_whitespace_name_validation(self):
        """Test validation with whitespace-only name"""
        with pytest.raises(ValueError, match="Artist name is required"):
            MockArtistCreateDTO(name="   ")
    
    def test_long_name_validation(self):
        """Test validation with too long name"""
        long_name = "A" * 201
        with pytest.raises(ValueError, match="Artist name too long"):
            MockArtistCreateDTO(name=long_name)


class TestArtistResponseDTO:
    """Test artist response DTO"""
    
    def test_response_dto_creation(self):
        """Test creating response DTO"""
        dto = MockArtistResponseDTO(
            id=1,
            name="Response Artist",
            bio="Artist bio",
            status=MockArtistStatus.ACTIVE
        )
        assert dto.id == 1
        assert dto.name == "Response Artist"
        assert dto.bio == "Artist bio"
        assert dto.status == MockArtistStatus.ACTIVE
        assert dto.created_at is not None
    
    def test_to_dict_conversion(self):
        """Test converting DTO to dictionary"""
        dto = MockArtistResponseDTO(
            id=1,
            name="Dict Artist",
            status=MockArtistStatus.PENDING
        )
        result = dto.to_dict()
        
        assert result["id"] == 1
        assert result["name"] == "Dict Artist"
        assert result["status"] == "pending"
        assert "created_at" in result
    
    def test_default_status(self):
        """Test default status assignment"""
        dto = MockArtistResponseDTO(id=1, name="Default Status")
        assert dto.status == MockArtistStatus.ACTIVE


class TestArtistListDTO:
    """Test artist list DTO"""
    
    def test_empty_list_creation(self):
        """Test creating empty artist list"""
        dto = MockArtistListDTO()
        assert len(dto.artists) == 0
        assert dto.total_count == 0
        assert dto.page == 1
        assert dto.page_size == 10
    
    def test_add_artist_to_list(self):
        """Test adding artist to list"""
        list_dto = MockArtistListDTO()
        artist = MockArtistResponseDTO(id=1, name="List Artist")
        
        list_dto.add_artist(artist)
        
        assert len(list_dto.artists) == 1
        assert list_dto.total_count == 1
        assert list_dto.artists[0].name == "List Artist"
    
    def test_multiple_artists_in_list(self):
        """Test adding multiple artists"""
        list_dto = MockArtistListDTO()
        
        for i in range(3):
            artist = MockArtistResponseDTO(id=i+1, name=f"Artist {i+1}")
            list_dto.add_artist(artist)
        
        assert len(list_dto.artists) == 3
        assert list_dto.total_count == 3


class TestArtistMapper:
    """Test artist mapper functionality"""
    
    def test_create_dto_to_entity_mapping(self):
        """Test mapping create DTO to entity"""
        dto = MockArtistCreateDTO(
            name="Mapper Artist",
            bio="Mapper bio",
            spotify_id="spotify123"
        )
        
        entity_data = MockArtistMapper.create_dto_to_entity(dto)
        
        assert entity_data["name"] == "Mapper Artist"
        assert entity_data["bio"] == "Mapper bio"
        assert entity_data["spotify_id"] == "spotify123"
        assert entity_data["image_url"] is None
    
    def test_entity_to_response_dto_mapping(self):
        """Test mapping entity to response DTO"""
        entity_data = {
            "id": 1,
            "name": "Entity Artist",
            "bio": "Entity bio",
            "status": "inactive",
            "created_at": datetime(2024, 1, 1)
        }
        
        dto = MockArtistMapper.entity_to_response_dto(entity_data)
        
        assert dto.id == 1
        assert dto.name == "Entity Artist"
        assert dto.bio == "Entity bio"
        assert dto.status == MockArtistStatus.INACTIVE
        assert dto.created_at == datetime(2024, 1, 1)
    
    def test_entity_mapping_with_defaults(self):
        """Test entity mapping with missing fields"""
        entity_data = {"id": 2, "name": "Minimal Entity"}
        
        dto = MockArtistMapper.entity_to_response_dto(entity_data)
        
        assert dto.id == 2
        assert dto.name == "Minimal Entity"
        assert dto.bio is None
        assert dto.status == MockArtistStatus.ACTIVE
        assert dto.created_at is not None


class TestArtistIntegration:
    """Integration tests for artist DTOs and mappers"""
    
    def test_full_artist_workflow(self):
        """Test complete artist creation and response workflow"""
        # Create DTO
        create_dto = MockArtistCreateDTO(
            name="Workflow Artist",
            bio="Workflow bio"
        )
        
        # Map to entity
        entity_data = MockArtistMapper.create_dto_to_entity(create_dto)
        entity_data["id"] = 1  # Simulate database ID assignment
        
        # Map back to response DTO
        response_dto = MockArtistMapper.entity_to_response_dto(entity_data)
        
        # Verify workflow
        assert response_dto.id == 1
        assert response_dto.name == "Workflow Artist"
        assert response_dto.bio == "Workflow bio"
        assert response_dto.status == MockArtistStatus.ACTIVE
    
    def test_artist_list_workflow(self):
        """Test artist list creation workflow"""
        # Create list
        artist_list = MockArtistListDTO(page=2, page_size=5)
        
        # Add artists
        for i in range(3):
            artist = MockArtistResponseDTO(
                id=i+1,
                name=f"List Artist {i+1}",
                status=MockArtistStatus.ACTIVE
            )
            artist_list.add_artist(artist)
        
        # Verify list
        assert len(artist_list.artists) == 3
        assert artist_list.total_count == 3
        assert artist_list.page == 2
        assert artist_list.page_size == 5
        
        # Verify first artist
        first_artist = artist_list.artists[0]
        assert first_artist.name == "List Artist 1"
        assert first_artist.status == MockArtistStatus.ACTIVE
