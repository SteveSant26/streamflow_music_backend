"""
Tests for common services and adapters
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import json
from enum import Enum


class MockServiceStatus(Enum):
    """Mock service status enumeration"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    PROCESSING = "processing"


class MockMediaFormat(Enum):
    """Mock media format enumeration"""
    MP3 = "mp3"
    MP4 = "mp4"
    WAV = "wav"
    FLAC = "flac"


@dataclass
class MockTrackInfo:
    """Mock track information data class"""
    title: str
    artist: str
    album: Optional[str] = None
    duration: Optional[int] = None
    url: str = ""
    thumbnail_url: Optional[str] = None
    format: MockMediaFormat = MockMediaFormat.MP3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration": self.duration,
            "url": self.url,
            "thumbnail_url": self.thumbnail_url,
            "format": self.format.value
        }


@dataclass
class MockDownloadResult:
    """Mock download result data class"""
    success: bool
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    track_info: Optional[MockTrackInfo] = None
    
    def is_valid(self) -> bool:
        """Check if download result is valid"""
        return self.success and self.file_path is not None


class MockYouTubeService:
    """Mock YouTube service for testing"""
    
    def __init__(self):
        self.status = MockServiceStatus.AVAILABLE
        self._mock_data = {}
    
    def search_track(self, query: str) -> List[MockTrackInfo]:
        """Mock search track functionality"""
        if self.status != MockServiceStatus.AVAILABLE:
            raise ConnectionError("YouTube service unavailable")
        
        if not query or len(query.strip()) == 0:
            return []
        
        # Simulate search results
        results = []
        for i in range(min(3, len(query.split()))):  # Max 3 results
            track = MockTrackInfo(
                title=f"Result {i+1} for {query}",
                artist=f"Artist {i+1}",
                album=f"Album {i+1}",
                duration=180 + i * 30,
                url=f"https://youtube.com/watch?v={query}_{i}",
                thumbnail_url=f"https://img.youtube.com/vi/{query}_{i}/default.jpg"
            )
            results.append(track)
        
        return results
    
    def get_track_info(self, url: str) -> Optional[MockTrackInfo]:
        """Mock get track info functionality"""
        if self.status != MockServiceStatus.AVAILABLE:
            raise ConnectionError("YouTube service unavailable")
        
        if not url or "youtube.com" not in url:
            return None
        
        # Extract video ID from URL
        video_id = url.split("=")[-1] if "=" in url else "unknown"
        
        return MockTrackInfo(
            title=f"Track from {video_id}",
            artist="YouTube Artist",
            duration=240,
            url=url,
            thumbnail_url=f"https://img.youtube.com/vi/{video_id}/default.jpg"
        )
    
    def download_audio(self, url: str, output_path: str = "") -> MockDownloadResult:
        """Mock download audio functionality"""
        if self.status != MockServiceStatus.AVAILABLE:
            return MockDownloadResult(
                success=False,
                error_message="Service unavailable"
            )
        
        if not url or "youtube.com" not in url:
            return MockDownloadResult(
                success=False,
                error_message="Invalid URL"
            )
        
        # Simulate successful download
        video_id = url.split("=")[-1] if "=" in url else "unknown"
        file_path = f"{output_path}/{video_id}.mp3" if output_path else f"{video_id}.mp3"
        
        track_info = self.get_track_info(url)
        
        return MockDownloadResult(
            success=True,
            file_path=file_path,
            track_info=track_info
        )


class MockSpotifyService:
    """Mock Spotify service for testing"""
    
    def __init__(self):
        self.status = MockServiceStatus.AVAILABLE
        self._authenticated = True
    
    def search_track(self, query: str) -> List[MockTrackInfo]:
        """Mock Spotify search functionality"""
        if not self._authenticated:
            raise PermissionError("Spotify not authenticated")
        
        if self.status != MockServiceStatus.AVAILABLE:
            raise ConnectionError("Spotify service unavailable")
        
        if not query:
            return []
        
        # Simulate Spotify search results
        results = []
        words = query.split()
        for i, word in enumerate(words[:2]):  # Max 2 results
            track = MockTrackInfo(
                title=f"Spotify {word} Track",
                artist=f"Spotify Artist {i+1}",
                album=f"Spotify Album {i+1}",
                duration=200 + i * 20,
                url=f"https://open.spotify.com/track/{word}_{i}",
                format=MockMediaFormat.MP3
            )
            results.append(track)
        
        return results
    
    def get_track_details(self, spotify_id: str) -> Optional[MockTrackInfo]:
        """Mock get track details functionality"""
        if not self._authenticated:
            raise PermissionError("Spotify not authenticated")
        
        if not spotify_id:
            return None
        
        return MockTrackInfo(
            title=f"Track {spotify_id}",
            artist="Spotify Artist",
            album="Spotify Album",
            duration=180,
            url=f"https://open.spotify.com/track/{spotify_id}",
            format=MockMediaFormat.MP3
        )
    
    def authenticate(self) -> bool:
        """Mock authentication"""
        self._authenticated = True
        return True
    
    def is_authenticated(self) -> bool:
        """Check authentication status"""
        return self._authenticated


class MockUnifiedMusicService:
    """Mock unified music service that combines multiple sources"""
    
    def __init__(self):
        self.youtube_service = MockYouTubeService()
        self.spotify_service = MockSpotifyService()
        self.status = MockServiceStatus.AVAILABLE
    
    def search_all_sources(self, query: str) -> Dict[str, List[MockTrackInfo]]:
        """Search across all music sources"""
        if self.status != MockServiceStatus.AVAILABLE:
            raise ConnectionError("Unified service unavailable")
        
        results = {
            "youtube": [],
            "spotify": []
        }
        
        try:
            results["youtube"] = self.youtube_service.search_track(query)
        except Exception as e:
            results["youtube"] = []
        
        try:
            results["spotify"] = self.spotify_service.search_track(query)
        except Exception as e:
            results["spotify"] = []
        
        return results
    
    def get_best_match(self, query: str) -> Optional[MockTrackInfo]:
        """Get the best match across all sources"""
        all_results = self.search_all_sources(query)
        
        # Combine all results
        combined_results = []
        for source, tracks in all_results.items():
            combined_results.extend(tracks)
        
        if not combined_results:
            return None
        
        # Return first result as "best match"
        return combined_results[0]
    
    def download_from_best_source(self, query: str, output_path: str = "") -> MockDownloadResult:
        """Download from the best available source"""
        best_match = self.get_best_match(query)
        
        if not best_match:
            return MockDownloadResult(
                success=False,
                error_message="No matches found"
            )
        
        # Try YouTube download first
        if "youtube.com" in best_match.url:
            return self.youtube_service.download_audio(best_match.url, output_path)
        
        # For other sources, simulate download
        file_path = f"{output_path}/unified_{query.replace(' ', '_')}.mp3"
        return MockDownloadResult(
            success=True,
            file_path=file_path,
            track_info=best_match
        )


class MockLyricsService:
    """Mock lyrics service for testing"""
    
    def __init__(self):
        self.status = MockServiceStatus.AVAILABLE
        self._cache = {}
    
    def get_lyrics(self, title: str, artist: str) -> Optional[str]:
        """Mock get lyrics functionality"""
        if self.status != MockServiceStatus.AVAILABLE:
            raise ConnectionError("Lyrics service unavailable")
        
        if not title or not artist:
            return None
        
        # Check cache first
        cache_key = f"{artist.lower()}_{title.lower()}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Simulate lyrics retrieval
        lyrics = f"""[Verse 1]
This is a sample lyric for {title}
By the artist {artist}
Generated for testing purposes

[Chorus]
Sample lyrics, sample lyrics
Testing the lyrics service
Sample lyrics, sample lyrics
Everything works perfectly

[Verse 2]
Another verse for {title}
More testing lyrics here
Quality assurance lyrics
For the {artist} track"""
        
        # Cache the result
        self._cache[cache_key] = lyrics
        return lyrics
    
    def search_lyrics(self, query: str) -> List[Dict[str, Any]]:
        """Mock search lyrics functionality"""
        if not query:
            return []
        
        results = []
        words = query.split()
        for i, word in enumerate(words[:3]):  # Max 3 results
            result = {
                "title": f"{word.title()} Song",
                "artist": f"Artist {i+1}",
                "lyrics_preview": f"Preview of lyrics containing {word}...",
                "confidence": 0.9 - i * 0.1
            }
            results.append(result)
        
        return results
    
    def clear_cache(self):
        """Clear lyrics cache"""
        self._cache.clear()


class TestYouTubeService:
    """Test YouTube service functionality"""
    
    def test_search_track_success(self):
        """Test successful track search"""
        service = MockYouTubeService()
        results = service.search_track("test song")
        
        assert len(results) == 2  # "test" and "song" words
        assert all(isinstance(track, MockTrackInfo) for track in results)
        assert results[0].title == "Result 1 for test song"
        assert results[0].artist == "Artist 1"
    
    def test_search_track_empty_query(self):
        """Test search with empty query"""
        service = MockYouTubeService()
        results = service.search_track("")
        
        assert len(results) == 0
    
    def test_search_track_service_unavailable(self):
        """Test search when service is unavailable"""
        service = MockYouTubeService()
        service.status = MockServiceStatus.UNAVAILABLE
        
        with pytest.raises(ConnectionError, match="YouTube service unavailable"):
            service.search_track("test")
    
    def test_get_track_info_success(self):
        """Test successful track info retrieval"""
        service = MockYouTubeService()
        url = "https://youtube.com/watch?v=test123"
        track_info = service.get_track_info(url)
        
        assert track_info is not None
        assert track_info.title == "Track from test123"
        assert track_info.artist == "YouTube Artist"
        assert track_info.url == url
    
    def test_get_track_info_invalid_url(self):
        """Test track info with invalid URL"""
        service = MockYouTubeService()
        track_info = service.get_track_info("invalid-url")
        
        assert track_info is None
    
    def test_download_audio_success(self):
        """Test successful audio download"""
        service = MockYouTubeService()
        url = "https://youtube.com/watch?v=download123"
        result = service.download_audio(url, "/output")
        
        assert result.success is True
        assert result.file_path == "/output/download123.mp3"
        assert result.track_info is not None
        assert result.is_valid() is True
    
    def test_download_audio_service_unavailable(self):
        """Test download when service is unavailable"""
        service = MockYouTubeService()
        service.status = MockServiceStatus.UNAVAILABLE
        
        result = service.download_audio("https://youtube.com/watch?v=test")
        
        assert result.success is False
        assert result.error_message == "Service unavailable"
        assert result.is_valid() is False


class TestSpotifyService:
    """Test Spotify service functionality"""
    
    def test_search_track_success(self):
        """Test successful Spotify track search"""
        service = MockSpotifyService()
        results = service.search_track("test song")
        
        assert len(results) == 2  # "test" and "song" words
        assert results[0].title == "Spotify test Track"
        assert results[0].artist == "Spotify Artist 1"
    
    def test_search_track_not_authenticated(self):
        """Test search when not authenticated"""
        service = MockSpotifyService()
        service._authenticated = False
        
        with pytest.raises(PermissionError, match="Spotify not authenticated"):
            service.search_track("test")
    
    def test_get_track_details_success(self):
        """Test successful track details retrieval"""
        service = MockSpotifyService()
        track_info = service.get_track_details("test_id")
        
        assert track_info is not None
        assert track_info.title == "Track test_id"
        assert track_info.artist == "Spotify Artist"
    
    def test_authentication(self):
        """Test authentication functionality"""
        service = MockSpotifyService()
        service._authenticated = False
        
        assert service.is_authenticated() is False
        
        result = service.authenticate()
        assert result is True
        assert service.is_authenticated() is True


class TestUnifiedMusicService:
    """Test unified music service functionality"""
    
    def test_search_all_sources_success(self):
        """Test searching all sources successfully"""
        service = MockUnifiedMusicService()
        results = service.search_all_sources("test query")
        
        assert "youtube" in results
        assert "spotify" in results
        assert len(results["youtube"]) > 0
        assert len(results["spotify"]) > 0
    
    def test_search_all_sources_with_failures(self):
        """Test searching with some sources failing"""
        service = MockUnifiedMusicService()
        service.youtube_service.status = MockServiceStatus.UNAVAILABLE
        
        results = service.search_all_sources("test")
        
        assert "youtube" in results
        assert "spotify" in results
        assert len(results["youtube"]) == 0  # Failed
        assert len(results["spotify"]) > 0  # Succeeded
    
    def test_get_best_match_success(self):
        """Test getting best match successfully"""
        service = MockUnifiedMusicService()
        best_match = service.get_best_match("test song")
        
        assert best_match is not None
        assert isinstance(best_match, MockTrackInfo)
    
    def test_get_best_match_no_results(self):
        """Test getting best match with no results"""
        service = MockUnifiedMusicService()
        service.youtube_service.status = MockServiceStatus.UNAVAILABLE
        service.spotify_service.status = MockServiceStatus.UNAVAILABLE
        
        best_match = service.get_best_match("test")
        
        assert best_match is None
    
    def test_download_from_best_source_success(self):
        """Test downloading from best source successfully"""
        service = MockUnifiedMusicService()
        result = service.download_from_best_source("test song", "/output")
        
        assert result.success is True
        assert result.file_path is not None
        assert result.track_info is not None
    
    def test_download_from_best_source_no_match(self):
        """Test downloading when no match found"""
        service = MockUnifiedMusicService()
        service.status = MockServiceStatus.UNAVAILABLE
        
        with pytest.raises(ConnectionError, match="Unified service unavailable"):
            service.download_from_best_source("test")


class TestLyricsService:
    """Test lyrics service functionality"""
    
    def test_get_lyrics_success(self):
        """Test successful lyrics retrieval"""
        service = MockLyricsService()
        lyrics = service.get_lyrics("Test Song", "Test Artist")
        
        assert lyrics is not None
        assert "Test Song" in lyrics
        assert "Test Artist" in lyrics
        assert "[Verse 1]" in lyrics
        assert "[Chorus]" in lyrics
    
    def test_get_lyrics_cached(self):
        """Test lyrics retrieval from cache"""
        service = MockLyricsService()
        
        # First call
        lyrics1 = service.get_lyrics("Cached Song", "Cached Artist")
        
        # Second call should be from cache
        lyrics2 = service.get_lyrics("Cached Song", "Cached Artist")
        
        assert lyrics1 == lyrics2
        assert lyrics1 is not None
    
    def test_get_lyrics_empty_params(self):
        """Test lyrics retrieval with empty parameters"""
        service = MockLyricsService()
        
        lyrics1 = service.get_lyrics("", "Artist")
        lyrics2 = service.get_lyrics("Song", "")
        lyrics3 = service.get_lyrics("", "")
        
        assert lyrics1 is None
        assert lyrics2 is None
        assert lyrics3 is None
    
    def test_search_lyrics_success(self):
        """Test successful lyrics search"""
        service = MockLyricsService()
        results = service.search_lyrics("love song")
        
        assert len(results) == 2  # "love" and "song" words
        assert all("title" in result for result in results)
        assert all("artist" in result for result in results)
        assert all("confidence" in result for result in results)
        assert results[0]["title"] == "Love Song"
    
    def test_search_lyrics_empty_query(self):
        """Test lyrics search with empty query"""
        service = MockLyricsService()
        results = service.search_lyrics("")
        
        assert len(results) == 0
    
    def test_clear_cache(self):
        """Test clearing lyrics cache"""
        service = MockLyricsService()
        
        # Add to cache
        service.get_lyrics("Cache Test", "Cache Artist")
        
        # Clear cache
        service.clear_cache()
        
        # Verify cache is empty
        assert len(service._cache) == 0


class TestServiceIntegration:
    """Integration tests for services"""
    
    def test_multi_service_workflow(self):
        """Test workflow using multiple services"""
        # Initialize services
        youtube = MockYouTubeService()
        spotify = MockSpotifyService()
        unified = MockUnifiedMusicService()
        lyrics = MockLyricsService()
        
        # Search for a song
        query = "test integration song"
        
        # Get results from unified service
        all_results = unified.search_all_sources(query)
        assert "youtube" in all_results
        assert "spotify" in all_results
        
        # Get best match
        best_match = unified.get_best_match(query)
        assert best_match is not None
        
        # Get lyrics for the best match
        song_lyrics = lyrics.get_lyrics(best_match.title, best_match.artist)
        assert song_lyrics is not None
        assert best_match.title in song_lyrics
        
        # Download the song
        download_result = unified.download_from_best_source(query)
        assert download_result.success is True
        assert download_result.is_valid() is True
    
    def test_service_failure_handling(self):
        """Test handling of service failures"""
        # Initialize services with some failures
        unified = MockUnifiedMusicService()
        unified.youtube_service.status = MockServiceStatus.ERROR
        
        lyrics = MockLyricsService()
        lyrics.status = MockServiceStatus.UNAVAILABLE
        
        # Test graceful handling
        results = unified.search_all_sources("test")
        assert len(results["youtube"]) == 0  # Failed service
        assert len(results["spotify"]) > 0  # Working service
        
        # Test lyrics service failure
        with pytest.raises(ConnectionError):
            lyrics.get_lyrics("Test", "Artist")
    
    def test_data_consistency(self):
        """Test data consistency across services"""
        service = MockUnifiedMusicService()
        
        # Search and get results
        query = "consistency test"
        all_results = service.search_all_sources(query)
        
        # Verify all results have consistent structure
        for source, tracks in all_results.items():
            for track in tracks:
                assert hasattr(track, 'title')
                assert hasattr(track, 'artist')
                assert hasattr(track, 'url')
                
                # Test serialization
                track_dict = track.to_dict()
                assert 'title' in track_dict
                assert 'artist' in track_dict
                assert 'format' in track_dict
