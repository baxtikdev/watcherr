from __future__ import annotations

import hashlib
import threading
import time

_MAX_ENTRIES = 1024


class RateLimiter:
    def __init__(self, window_seconds: int = 60):
        self.window = window_seconds
        self._seen: dict[str, float] = {}
        self._lock = threading.Lock()

    def should_send(self, message: str) -> bool:
        key = hashlib.md5(message.encode()).hexdigest()
        now = time.monotonic()

        with self._lock:
            self._cleanup(now)
            if key in self._seen:
                return False
            self._seen[key] = now
            return True

    def _cleanup(self, now: float) -> None:
        expired = [k for k, t in self._seen.items() if now - t > self.window]
        for k in expired:
            del self._seen[k]

        if len(self._seen) > _MAX_ENTRIES:
            oldest = sorted(self._seen, key=self._seen.get)  # type: ignore[arg-type]
            for k in oldest[: len(self._seen) - _MAX_ENTRIES]:
                del self._seen[k]


_lock = threading.Lock()
_limiter: RateLimiter | None = None


def get_rate_limiter(window: int) -> RateLimiter:
    global _limiter
    with _lock:
        if _limiter is None or _limiter.window != window:
            _limiter = RateLimiter(window)
        return _limiter
