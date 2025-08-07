"""
Simple in-memory cache for song search results to avoid repeated YouTube API calls
"""

import threading
import time
from typing import Any, Dict, Optional


class PerformanceCache:
    """Simple thread-safe in-memory cache for performance optimization"""

    def __init__(self, default_ttl: int = 300):  # 5 minutes default TTL
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key not in self._cache:
                return None

            item = self._cache[key]
            if time.time() > item["expires_at"]:
                del self._cache[key]
                return None

            return item["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl

        with self._lock:
            self._cache[key] = {"value": value, "expires_at": expires_at}

    def clear(self) -> None:
        """Clear all cached items"""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Get current cache size"""
        with self._lock:
            return len(self._cache)

    def cleanup_expired(self) -> int:
        """Remove expired items and return count of removed items"""
        current_time = time.time()
        removed_count = 0

        with self._lock:
            expired_keys = [
                key
                for key, item in self._cache.items()
                if current_time > item["expires_at"]
            ]

            for key in expired_keys:
                del self._cache[key]
                removed_count += 1

        return removed_count


# Global cache instances
youtube_search_cache = PerformanceCache(
    default_ttl=600
)  # 10 minutes for YouTube searches
song_processing_cache = PerformanceCache(
    default_ttl=1800
)  # 30 minutes for processed songs
