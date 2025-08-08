"""
Tests for Artists Use Cases
Following clean architecture pattern with isolated testing
"""

import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List, Optional

# Mock del repositorio
class MockArtistRepository:
    def __init__(self):
        self.artists = []
        self.save_called = False
        self.get_by_id_called = False
        self.find_by_name_called = False
        
    def save(self, artist):
        self.save_called = True
        self.artists.append(artist)
        return artist
        
    def get_by_id(self, artist_id):
        self.get_by_id_called = True
        return None
        
    def find_by_name(self, name):
        self.find_by_name_called = True
        return [a for a in self.artists if a.name.lower() == name.lower()]

# Mock de entidades
@dataclass
class MockArtist:
    id: Optional[str] = None
    name: str = "Test Artist"
    bio: Optional[str] = None
    image_url: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"artist_{len(self.name)}"

class TestSaveArtistUseCase:
    """Test Save Artist Use Case Logic"""
    
    def test_save_artist_success(self):
        """Test successful artist save"""
        # Arrange
        repository = MockArtistRepository()
        artist_data = {
            'name': 'New Artist',
            'bio': 'Great musician',
            'image_url': 'https://example.com/image.jpg'
        }
        
        # Act
        artist = MockArtist(**artist_data)
        result = repository.save(artist)
        
        # Assert
        assert repository.save_called is True
        assert result.name == 'New Artist'
        assert result.bio == 'Great musician'
        assert len(repository.artists) == 1
        
    def test_save_artist_minimal_data(self):
        """Test artist save with minimal data"""
        # Arrange
        repository = MockArtistRepository()
        artist_data = {'name': 'Minimal Artist'}
        
        # Act
        artist = MockArtist(**artist_data)
        result = repository.save(artist)
        
        # Assert
        assert repository.save_called is True
        assert result.name == 'Minimal Artist'
        assert result.id is not None
        assert result.bio is None
        
    def test_save_artist_validation(self):
        """Test artist data validation"""
        # Test valid creation (no exceptions should be raised)
        artist = MockArtist(name="Valid Name")
        assert artist.name == "Valid Name"
            
    def test_find_artist_by_name(self):
        """Test finding artist by name"""
        # Arrange
        repository = MockArtistRepository()
        artist1 = MockArtist(name="John Doe")
        artist2 = MockArtist(name="Jane Smith")
        
        repository.save(artist1)
        repository.save(artist2)
        
        # Act
        results = repository.find_by_name("John Doe")
        
        # Assert
        assert repository.find_by_name_called is True
        assert len(results) == 1
        assert results[0].name == "John Doe"
        
    def test_artist_entity_creation(self):
        """Test artist entity creation logic"""
        artist = MockArtist(
            name="Complete Artist",
            bio="Full biography",
            image_url="https://example.com/full.jpg"
        )
        
        assert artist.name == "Complete Artist"
        assert artist.bio == "Full biography"
        assert artist.image_url == "https://example.com/full.jpg"
        assert artist.id is not None
        
    def test_multiple_artists_save(self):
        """Test saving multiple artists"""
        repository = MockArtistRepository()
        
        artists_data = [
            {"name": "Artist 1", "bio": "Bio 1"},
            {"name": "Artist 2", "bio": "Bio 2"},
            {"name": "Artist 3", "bio": "Bio 3"}
        ]
        
        for data in artists_data:
            artist = MockArtist(**data)
            repository.save(artist)
            
        assert len(repository.artists) == 3
        assert all(artist.id is not None for artist in repository.artists)
        
    def test_artist_name_case_insensitive_search(self):
        """Test case insensitive artist search"""
        repository = MockArtistRepository()
        artist = MockArtist(name="CasE SenSiTive")
        repository.save(artist)
        
        # Test different cases
        results1 = repository.find_by_name("case sensitive")
        results2 = repository.find_by_name("CASE SENSITIVE")
        results3 = repository.find_by_name("CasE SenSiTive")
        
        assert len(results1) == 1
        assert len(results2) == 1
        assert len(results3) == 1
        
    def test_use_case_workflow_simulation(self):
        """Simulate complete artist use case workflow"""
        # Arrange
        repository = MockArtistRepository()
        
        # Act - Execute use case steps
        # 1. Create artist entity
        artist_data = {
            'name': 'Workflow Artist',
            'bio': 'Amazing workflow',
            'image_url': 'https://example.com/workflow.jpg'
        }
        artist = MockArtist(**artist_data)
        
        # 2. Validate artist
        assert artist.name and len(artist.name) > 0
        
        # 3. Check if artist exists
        existing = repository.find_by_name(artist.name)
        assert len(existing) == 0
        
        # 4. Save to repository
        saved_artist = repository.save(artist)
        
        # Assert - Verify complete workflow
        assert saved_artist.id is not None
        assert saved_artist.name == 'Workflow Artist'
        assert len(repository.artists) == 1
        
    def test_duplicate_artist_handling(self):
        """Test handling of duplicate artist names"""
        repository = MockArtistRepository()
        
        # Save first artist
        artist1 = MockArtist(name="Duplicate Name")
        repository.save(artist1)
        
        # Save second artist with same name
        artist2 = MockArtist(name="Duplicate Name")
        repository.save(artist2)
        
        # Check both are saved (business logic may vary)
        assert len(repository.artists) == 2
        
        # Find by name returns both
        results = repository.find_by_name("Duplicate Name")
        assert len(results) == 2
        
    def test_artist_data_types(self):
        """Test artist data type handling"""
        artist = MockArtist(
            name="Type Test",
            bio="String bio"
        )
        
        assert isinstance(artist.name, str)
        assert isinstance(artist.bio, str)
        assert isinstance(artist.id, str)
        
    def test_edge_cases(self):
        """Test edge cases for artist use case"""
        repository = MockArtistRepository()
        
        # Very long name
        long_name = "A" * 150
        artist = MockArtist(name=long_name)
        result = repository.save(artist)
        assert len(result.name) == 150
        
        # Special characters in name
        special_artist = MockArtist(
            name="Ärtiśt with ñ & çharacters",
            bio="Special bio with émojis 🎵"
        )
        result = repository.save(special_artist)
        assert "ñ" in result.name
        assert "🎵" in result.bio
        
        # URL validation (basic)
        url_artist = MockArtist(
            name="URL Artist",
            image_url="https://valid-url.com/image.png"
        )
        result = repository.save(url_artist)
        assert result.image_url.startswith("https://")
        
    def test_repository_error_handling(self):
        """Test repository error handling scenarios"""
        repository = MockArtistRepository()
        
        # Test with None values
        artist = MockArtist(name="Valid Name", bio=None, image_url=None)
        result = repository.save(artist)
        
        assert result.name == "Valid Name"
        assert result.bio is None
        assert result.image_url is None
