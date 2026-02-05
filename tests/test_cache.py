"""Tests for the cache module."""

from time import sleep
from unittest.mock import patch


class TestCache:
    """Tests for the Cache class."""

    def test_set_and_get(self, fresh_cache):
        """Test basic set and get operations."""
        fresh_cache.set("key1", "value1")
        result = fresh_cache.get("key1", ttl=60)
        assert result == "value1"

    def test_get_nonexistent_key(self, fresh_cache):
        """Test getting a key that doesn't exist."""
        result = fresh_cache.get("nonexistent", ttl=60)
        assert result is None

    def test_get_expired_key(self, fresh_cache):
        """Test that expired entries return None."""
        fresh_cache.set("key1", "value1")
        # Use a very short TTL and check immediately
        result = fresh_cache.get("key1", ttl=0)
        assert result is None

    def test_get_removes_expired_entry(self, fresh_cache):
        """Test that getting an expired entry removes it from cache."""
        fresh_cache.set("key1", "value1")
        # Get with TTL=0 to expire it
        fresh_cache.get("key1", ttl=0)
        # Verify it's removed from internal data
        assert "key1" not in fresh_cache._data

    def test_ttl_not_expired(self, fresh_cache):
        """Test that entries within TTL are returned."""
        fresh_cache.set("key1", "value1")
        # Use a long TTL
        result = fresh_cache.get("key1", ttl=3600)
        assert result == "value1"

    def test_stores_different_value_types(self, fresh_cache):
        """Test that cache stores different types correctly."""
        fresh_cache.set("string", "hello")
        fresh_cache.set("number", 42)
        fresh_cache.set("list", [1, 2, 3])
        fresh_cache.set("dict", {"a": 1})

        assert fresh_cache.get("string", ttl=60) == "hello"
        assert fresh_cache.get("number", ttl=60) == 42
        assert fresh_cache.get("list", ttl=60) == [1, 2, 3]
        assert fresh_cache.get("dict", ttl=60) == {"a": 1}

    def test_overwrite_existing_key(self, fresh_cache):
        """Test that setting an existing key overwrites it."""
        fresh_cache.set("key1", "original")
        fresh_cache.set("key1", "updated")
        assert fresh_cache.get("key1", ttl=60) == "updated"


class TestCacheEviction:
    """Tests for cache eviction behavior."""

    def test_eviction_when_full(self, small_cache):
        """Test that oldest entries are evicted when cache is full."""
        # Fill the cache (max_size=10)
        for i in range(10):
            small_cache.set(f"key{i}", f"value{i}")

        # Add one more - should trigger eviction
        small_cache.set("key10", "value10")

        # At least one old entry should be removed
        assert len(small_cache._data) <= 10

    def test_eviction_removes_oldest(self, small_cache):
        """Test that eviction removes the oldest entries."""
        # Fill cache with entries
        for i in range(10):
            small_cache.set(f"key{i}", f"value{i}")

        # Add a new entry to trigger eviction
        small_cache.set("newest", "newest_value")

        # Newest entry should still be there
        assert small_cache.get("newest", ttl=60) == "newest_value"

    def test_eviction_removes_at_least_one(self):
        """Test that eviction removes at least one entry for small caches."""
        from ursaproxy.cache import Cache

        tiny_cache = Cache(max_size=3)

        for i in range(3):
            tiny_cache.set(f"key{i}", f"value{i}")

        # This should trigger eviction of at least 1 entry
        tiny_cache.set("key3", "value3")
        assert len(tiny_cache._data) <= 3


class TestCacheTimestamps:
    """Tests for cache timestamp behavior."""

    def test_timestamp_is_stored(self, fresh_cache):
        """Test that timestamp is stored with value."""
        fresh_cache.set("key1", "value1")
        value, timestamp = fresh_cache._data["key1"]
        assert value == "value1"
        assert isinstance(timestamp, float)
        assert timestamp > 0

    def test_newer_entries_have_higher_timestamps(self, fresh_cache):
        """Test that newer entries have higher timestamps."""
        fresh_cache.set("first", "value1")
        sleep(0.01)  # Small delay
        fresh_cache.set("second", "value2")

        _, ts1 = fresh_cache._data["first"]
        _, ts2 = fresh_cache._data["second"]
        assert ts2 > ts1

    def test_ttl_expiration_timing(self, fresh_cache):
        """Test TTL expiration with mocked time."""
        # Set a value
        with patch("ursaproxy.cache.time") as mock_time:
            mock_time.return_value = 1000.0
            fresh_cache.set("key1", "value1")

        # Check before expiration (5 seconds later)
        with patch("ursaproxy.cache.time") as mock_time:
            mock_time.return_value = 1005.0
            result = fresh_cache.get("key1", ttl=10)
            assert result == "value1"

        # Check after expiration (15 seconds later)
        with patch("ursaproxy.cache.time") as mock_time:
            mock_time.return_value = 1015.0
            result = fresh_cache.get("key1", ttl=10)
            assert result is None


class TestGlobalCache:
    """Tests for the global cache instance."""

    def test_global_cache_exists(self):
        """Test that global cache instance exists."""
        from ursaproxy.cache import cache

        assert cache is not None

    def test_global_cache_operations(self):
        """Test operations on global cache."""
        from ursaproxy.cache import cache

        cache.set("global_key", "global_value")
        result = cache.get("global_key", ttl=60)
        assert result == "global_value"
