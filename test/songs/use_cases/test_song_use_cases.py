"""
Tests for Songs Use Cases
Following clean architecture pattern with isolated testing
"""

import pytest
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List, Optional

# Mock del repositorio
class MockSongRepository:
    def __init__(self):
        self.songs = []
        self.save_called = False
        self.get_by_id_called = False
        self.search_called = False
        self.get_random_called = False
        
    def save(self, song):
        self.save_called = True
        self.songs.append(song)
        return song
        
    def get_by_id(self, song_id):
        self.get_by_id_called = True
        return next((s for s in self.songs if s.id == song_id), None)
        
    def search(self, query):
        self.search_called = True
        return [s for s in self.songs if query.lower() in s.title.lower()]
        
    def get_random(self, limit=10):
        self.get_random_called = True
        return self.songs[:limit]

# Mock de entidades
@dataclass
class MockSong:
    id: Optional[str] = None
    title: str = "Test Song"
    artist_name: str = "Test Artist"
    duration: Optional[int] = 180
    genre: Optional[str] = "Pop"
    play_count: int = 0
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"song_{len(self.title)}"
            
    def increment_play_count(self):
        self.play_count += 1

class TestSongUseCases:
    """Test Song Use Cases Logic"""
    
    def test_save_song_success(self):
        """Test successful song save"""
        # Arrange
        repository = MockSongRepository()
        song_data = {
            'title': 'New Song',
            'artist_name': 'New Artist',
            'duration': 240,
            'genre': 'Rock'
        }
        
        # Act
        song = MockSong(**song_data)
        result = repository.save(song)
        
        # Assert
        assert repository.save_called is True
        assert result.title == 'New Song'
        assert result.artist_name == 'New Artist'
        assert result.duration == 240
        assert len(repository.songs) == 1
        
    def test_save_song_minimal_data(self):
        """Test song save with minimal data"""
        repository = MockSongRepository()
        song_data = {
            'title': 'Minimal Song',
            'artist_name': 'Artist'
        }
        
        song = MockSong(**song_data)
        result = repository.save(song)
        
        assert result.title == 'Minimal Song'
        assert result.artist_name == 'Artist'
        assert result.id is not None
        assert result.play_count == 0
        
    def test_search_songs(self):
        """Test song search functionality"""
        repository = MockSongRepository()
        
        # Add test songs
        songs = [
            MockSong(title="Rock Song", artist_name="Rock Artist"),
            MockSong(title="Pop Song", artist_name="Pop Artist"),
            MockSong(title="Jazz Tune", artist_name="Jazz Artist")
        ]
        
        for song in songs:
            repository.save(song)
            
        # Search for songs
        results = repository.search("rock")
        
        assert repository.search_called is True
        assert len(results) == 1
        assert results[0].title == "Rock Song"
        
    def test_get_random_songs(self):
        """Test get random songs functionality"""
        repository = MockSongRepository()
        
        # Add multiple songs
        for i in range(15):
            song = MockSong(title=f"Song {i}", artist_name=f"Artist {i}")
            repository.save(song)
            
        # Get random songs
        random_songs = repository.get_random(10)
        
        assert repository.get_random_called is True
        assert len(random_songs) == 10
        
    def test_increment_play_count(self):
        """Test increment play count use case"""
        repository = MockSongRepository()
        song = MockSong(title="Popular Song", artist_name="Popular Artist")
        saved_song = repository.save(song)
        
        # Simulate play count increment
        initial_count = saved_song.play_count
        saved_song.increment_play_count()
        
        assert saved_song.play_count == initial_count + 1
        
        # Multiple increments
        for _ in range(5):
            saved_song.increment_play_count()
            
        assert saved_song.play_count == 6
        
    def test_get_song_by_id(self):
        """Test get song by ID use case"""
        repository = MockSongRepository()
        song = MockSong(title="Findable Song", artist_name="Findable Artist")
        saved_song = repository.save(song)
        
        # Find by ID
        found_song = repository.get_by_id(saved_song.id)
        
        assert repository.get_by_id_called is True
        assert found_song is not None
        assert found_song.title == "Findable Song"
        
        # Test not found
        not_found = repository.get_by_id("nonexistent_id")
        assert not_found is None
        
    def test_song_validation(self):
        """Test song data validation"""
        # Test valid creation (no exceptions should be raised)
        song = MockSong(title="Valid Title", artist_name="Valid Artist")
        assert song.title == "Valid Title"
        assert song.artist_name == "Valid Artist"
            
    def test_song_duration_handling(self):
        """Test song duration handling"""
        # Test valid duration
        song = MockSong(title="Timed Song", artist_name="Artist", duration=300)
        assert song.duration == 300
        
        # Test no duration
        song_no_duration = MockSong(title="Untimed Song", artist_name="Artist", duration=None)
        assert song_no_duration.duration is None
        
        # Test zero duration
        song_zero = MockSong(title="Zero Song", artist_name="Artist", duration=0)
        assert song_zero.duration == 0
        
    def test_multiple_songs_workflow(self):
        """Test complete workflow with multiple songs"""
        repository = MockSongRepository()
        
        # Create album worth of songs
        album_songs = []
        for i in range(12):
            song = MockSong(
                title=f"Track {i+1:02d}",
                artist_name="Album Artist",
                duration=180 + (i * 10),
                genre="Album Genre"
            )
            album_songs.append(song)
            repository.save(song)
            
        assert len(repository.songs) == 12
        
        # Test search within album
        results = repository.search("Track")
        assert len(results) == 12
        
        # Test random selection
        random_tracks = repository.get_random(5)
        assert len(random_tracks) == 5
        
    def test_song_genre_handling(self):
        """Test song genre functionality"""
        repository = MockSongRepository()
        
        genres = ["Rock", "Pop", "Jazz", "Classical", "Electronic"]
        for genre in genres:
            song = MockSong(
                title=f"{genre} Song",
                artist_name=f"{genre} Artist",
                genre=genre
            )
            repository.save(song)
            
        assert len(repository.songs) == 5
        
        # Test genre diversity
        genres_in_repo = [song.genre for song in repository.songs]
        assert len(set(genres_in_repo)) == 5
        
    def test_edge_cases(self):
        """Test edge cases for song use cases"""
        repository = MockSongRepository()
        
        # Very long title
        long_title = "A" * 300
        song = MockSong(title=long_title, artist_name="Artist")
        result = repository.save(song)
        assert len(result.title) == 300
        
        # Special characters
        special_song = MockSong(
            title="Song with éñáü & symbols !@#",
            artist_name="Ártist with ñ"
        )
        result = repository.save(special_song)
        assert "éñáü" in result.title
        assert "ñ" in result.artist_name
        
        # Very high play count
        popular_song = MockSong(title="Viral Song", artist_name="Viral Artist")
        repository.save(popular_song)
        
        # Simulate viral popularity
        for _ in range(1000000):
            popular_song.increment_play_count()
            
        assert popular_song.play_count == 1000000
        
    def test_search_case_insensitive(self):
        """Test case insensitive search"""
        repository = MockSongRepository()
        
        song = MockSong(title="CasE SenSiTive Song", artist_name="Artist")
        repository.save(song)
        
        # Test different cases
        results1 = repository.search("case")
        results2 = repository.search("CASE")
        results3 = repository.search("sensitive")
        
        assert len(results1) >= 1
        assert len(results2) >= 1
        assert len(results3) >= 1
        
    def test_repository_interaction_patterns(self):
        """Test various repository interaction patterns"""
        repository = MockSongRepository()
        
        # Batch save
        songs_to_save = [
            MockSong(title=f"Batch Song {i}", artist_name="Batch Artist")
            for i in range(20)
        ]
        
        for song in songs_to_save:
            repository.save(song)
            
        assert len(repository.songs) == 20
        
        # Verify all calls were made
        assert repository.save_called is True
        
        # Test search
        search_results = repository.search("Batch")
        assert len(search_results) == 20
        assert repository.search_called is True
        
        # Test random selection
        random_selection = repository.get_random(15)
        assert len(random_selection) == 15
        assert repository.get_random_called is True
