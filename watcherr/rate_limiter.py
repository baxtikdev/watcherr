from __future__ import annotations

import hashlib
import threading
import time


class RateLimiter:
    def __init__(self, window_seconds: int = 60):
        self._window = window_seconds
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
        expired = [k for k, t in self._seen.items() if now - t > self._window]
        for k in expired:
            del self._seen[k]


_limiter: RateLimiter | None = None


def get_rate_limiter(window: int) -> RateLimiter:
    global _limiter
    if _limiter is None or _limiter._window != window:
        _limiter = RateLimiter(window)
    return _limiter
