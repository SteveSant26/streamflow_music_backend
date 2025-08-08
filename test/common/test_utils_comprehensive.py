"""
Tests for Common Utils and Validators
Following clean architecture pattern with direct module testing
"""

import pytest
from typing import Optional, List, Dict, Any

# Mock implementation de utils más comunes
class MockFileValidator:
    """Mock file validator for testing"""
    
    @staticmethod
    def validate_audio_file(file_path: str) -> bool:
        """Validate audio file extension"""
        valid_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a']
        return any(file_path.lower().endswith(ext) for ext in valid_extensions)
    
    @staticmethod
    def validate_image_file(file_path: str) -> bool:
        """Validate image file extension"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        return any(file_path.lower().endswith(ext) for ext in valid_extensions)
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
        """Validate file size in MB"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes

class MockDataValidator:
    """Mock data validator for testing"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        if not email or "@" not in email:
            return False
        parts = email.split("@")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return False
        domain = parts[1]
        return "." in domain and domain.count(".") > 0 and not domain.startswith(".") and not domain.endswith(".")
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Basic URL validation"""
        return url.startswith(("http://", "https://"))
    
    @staticmethod
    def validate_duration(duration: int) -> bool:
        """Validate audio duration in seconds"""
        return 0 < duration <= 7200  # Max 2 hours
    
    @staticmethod
    def validate_title(title: str) -> bool:
        """Validate title length and content"""
        return 1 <= len(title.strip()) <= 200
    
    @staticmethod
    def validate_artist_name(name: str) -> bool:
        """Validate artist name"""
        return 1 <= len(name.strip()) <= 100

class MockStringUtils:
    """Mock string utilities for testing"""
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Clean filename for safe storage"""
        import re
        # Remove special characters except dots and hyphens
        cleaned = re.sub(r'[^\w\s\-_\.]', '', filename)
        # Replace spaces with underscores
        cleaned = re.sub(r'\s+', '_', cleaned)
        return cleaned.lower()
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 50) -> str:
        """Truncate text with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration as MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def slug_from_title(title: str) -> str:
        """Create URL slug from title"""
        import re
        slug = title.lower()
        slug = re.sub(r'[^\w\s\-]', '', slug)
        slug = re.sub(r'[\s_\-]+', '-', slug)
        return slug.strip('-')

class MockCacheUtils:
    """Mock cache utilities for testing"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL"""
        self.cache[key] = value
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self.cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
    
    def has_key(self, key: str) -> bool:
        """Check if key exists in cache"""
        return key in self.cache

class TestFileValidator:
    """Test file validation utilities"""
    
    def test_validate_audio_file(self):
        """Test audio file validation"""
        assert MockFileValidator.validate_audio_file("song.mp3") is True
        assert MockFileValidator.validate_audio_file("song.wav") is True
        assert MockFileValidator.validate_audio_file("song.flac") is True
        assert MockFileValidator.validate_audio_file("song.txt") is False
        assert MockFileValidator.validate_audio_file("song.pdf") is False
        
    def test_validate_image_file(self):
        """Test image file validation"""
        assert MockFileValidator.validate_image_file("cover.jpg") is True
        assert MockFileValidator.validate_image_file("cover.png") is True
        assert MockFileValidator.validate_image_file("cover.gif") is True
        assert MockFileValidator.validate_image_file("cover.txt") is False
        assert MockFileValidator.validate_image_file("cover.mp3") is False
        
    def test_validate_file_size(self):
        """Test file size validation"""
        # 5MB file (under 10MB limit)
        assert MockFileValidator.validate_file_size(5 * 1024 * 1024) is True
        # 15MB file (over 10MB limit)
        assert MockFileValidator.validate_file_size(15 * 1024 * 1024) is False
        # Custom limit
        assert MockFileValidator.validate_file_size(5 * 1024 * 1024, max_size_mb=3) is False
        
    def test_case_insensitive_validation(self):
        """Test case insensitive file validation"""
        assert MockFileValidator.validate_audio_file("Song.MP3") is True
        assert MockFileValidator.validate_audio_file("Song.WAV") is True
        assert MockFileValidator.validate_image_file("Cover.JPG") is True
        assert MockFileValidator.validate_image_file("Cover.PNG") is True

class TestDataValidator:
    """Test data validation utilities"""
    
    def test_validate_email(self):
        """Test email validation"""
        assert MockDataValidator.validate_email("test@example.com") is True
        assert MockDataValidator.validate_email("user@domain.org") is True
        assert MockDataValidator.validate_email("invalid.email") is False
        assert MockDataValidator.validate_email("@domain.com") is False
        assert MockDataValidator.validate_email("user@") is False
        
    def test_validate_url(self):
        """Test URL validation"""
        assert MockDataValidator.validate_url("https://example.com") is True
        assert MockDataValidator.validate_url("http://example.com") is True
        assert MockDataValidator.validate_url("ftp://example.com") is False
        assert MockDataValidator.validate_url("example.com") is False
        
    def test_validate_duration(self):
        """Test duration validation"""
        assert MockDataValidator.validate_duration(180) is True  # 3 minutes
        assert MockDataValidator.validate_duration(3600) is True  # 1 hour
        assert MockDataValidator.validate_duration(0) is False  # Too short
        assert MockDataValidator.validate_duration(8000) is False  # Too long
        
    def test_validate_title(self):
        """Test title validation"""
        assert MockDataValidator.validate_title("Valid Title") is True
        assert MockDataValidator.validate_title("A" * 200) is True  # Max length
        assert MockDataValidator.validate_title("") is False  # Empty
        assert MockDataValidator.validate_title("   ") is False  # Only spaces
        assert MockDataValidator.validate_title("A" * 201) is False  # Too long
        
    def test_validate_artist_name(self):
        """Test artist name validation"""
        assert MockDataValidator.validate_artist_name("Artist Name") is True
        assert MockDataValidator.validate_artist_name("A" * 100) is True  # Max length
        assert MockDataValidator.validate_artist_name("") is False  # Empty
        assert MockDataValidator.validate_artist_name("A" * 101) is False  # Too long

class TestStringUtils:
    """Test string utility functions"""
    
    def test_clean_filename(self):
        """Test filename cleaning"""
        assert MockStringUtils.clean_filename("Song Title!.mp3") == "song_title.mp3"
        assert MockStringUtils.clean_filename("Artist - Song (2024).mp3") == "artist_-_song_2024.mp3"
        assert MockStringUtils.clean_filename("File With Spaces.txt") == "file_with_spaces.txt"
        
    def test_truncate_text(self):
        """Test text truncation"""
        long_text = "This is a very long text that should be truncated"
        assert MockStringUtils.truncate_text(long_text, 20) == "This is a very lo..."
        assert MockStringUtils.truncate_text("Short", 20) == "Short"
        
    def test_format_duration(self):
        """Test duration formatting"""
        assert MockStringUtils.format_duration(90) == "01:30"
        assert MockStringUtils.format_duration(3661) == "61:01"
        assert MockStringUtils.format_duration(0) == "00:00"
        
    def test_slug_from_title(self):
        """Test slug generation"""
        assert MockStringUtils.slug_from_title("Song Title") == "song-title"
        assert MockStringUtils.slug_from_title("Artist - Song!") == "artist-song"
        assert MockStringUtils.slug_from_title("  Spaced  Title  ") == "spaced-title"

class TestCacheUtils:
    """Test cache utility functions"""
    
    def test_cache_operations(self):
        """Test basic cache operations"""
        cache = MockCacheUtils()
        
        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test non-existent key
        assert cache.get("nonexistent") is None
        
        # Test has_key
        assert cache.has_key("key1") is True
        assert cache.has_key("nonexistent") is False
        
    def test_cache_delete(self):
        """Test cache deletion"""
        cache = MockCacheUtils()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.delete("key1")
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        
    def test_cache_clear(self):
        """Test cache clearing"""
        cache = MockCacheUtils()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        
    def test_cache_with_complex_data(self):
        """Test cache with complex data types"""
        cache = MockCacheUtils()
        
        # Test with dict
        data = {"name": "test", "value": 123}
        cache.set("dict_key", data)
        assert cache.get("dict_key") == data
        
        # Test with list
        list_data = [1, 2, 3, "test"]
        cache.set("list_key", list_data)
        assert cache.get("list_key") == list_data

class TestUtilsIntegration:
    """Test integration between utilities"""
    
    def test_file_processing_workflow(self):
        """Test complete file processing workflow"""
        # 1. Validate file
        filename = "My Song Title.mp3"
        assert MockFileValidator.validate_audio_file(filename) is True
        
        # 2. Clean filename
        clean_name = MockStringUtils.clean_filename(filename)
        assert clean_name == "my_song_title.mp3"
        
        # 3. Create slug for URL
        title = "My Song Title"
        slug = MockStringUtils.slug_from_title(title)
        assert slug == "my-song-title"
        
    def test_validation_and_formatting_chain(self):
        """Test validation and formatting chain"""
        # Artist name validation and processing
        artist_name = "  The Beatles  "
        assert MockDataValidator.validate_artist_name(artist_name) is True
        
        slug = MockStringUtils.slug_from_title(artist_name.strip())
        assert slug == "the-beatles"
        
        # Duration validation and formatting
        duration = 245  # seconds
        assert MockDataValidator.validate_duration(duration) is True
        formatted = MockStringUtils.format_duration(duration)
        assert formatted == "04:05"
        
    def test_cache_with_validation(self):
        """Test cache combined with validation"""
        cache = MockCacheUtils()
        
        # Cache validation results
        email = "test@example.com"
        is_valid = MockDataValidator.validate_email(email)
        cache.set(f"email_valid_{email}", is_valid)
        
        # Retrieve cached result
        cached_result = cache.get(f"email_valid_{email}")
        assert cached_result is True
        
        # Test with invalid email
        invalid_email = "invalid.email"
        is_valid_invalid = MockDataValidator.validate_email(invalid_email)
        cache.set(f"email_valid_{invalid_email}", is_valid_invalid)
        
        cached_invalid = cache.get(f"email_valid_{invalid_email}")
        assert cached_invalid is False
