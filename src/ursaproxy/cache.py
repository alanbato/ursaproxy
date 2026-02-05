from time import time
from typing import Any


class Cache:
    """Simple TTL cache using dict + timestamps with size limit."""

    def __init__(self, max_size: int = 1000) -> None:
        self._data: dict[str, tuple[Any, float]] = {}
        self._max_size = max_size

    def get(self, key: str, ttl: int) -> Any | None:
        """Get value if exists and not expired."""
        entry = self._data.get(key)
        if entry:
            value, timestamp = entry
            if time() - timestamp < ttl:
                return value
            # Use pop to avoid race conditions
            self._data.pop(key, None)
        return None

    def set(self, key: str, value: Any) -> None:
        """Set value with current timestamp."""
        self._evict_if_full()
        self._data[key] = (value, time())

    def _evict_if_full(self) -> None:
        """Remove oldest entries if cache is full."""
        if len(self._data) >= self._max_size:
            # Remove oldest 10% of entries
            sorted_keys = sorted(self._data.keys(), key=lambda k: self._data[k][1])
            for key in sorted_keys[: len(sorted_keys) // 10 or 1]:
                self._data.pop(key, None)


cache = Cache()
