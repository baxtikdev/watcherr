# Changelog

## [0.3.0] - 2026-03-16

### Added
- Copyable code blocks in Telegram alerts (`<pre><code class="language-...">`) with syntax highlighting
- Auto language detection for tracebacks: Python, Java, JavaScript, Go, Ruby, JSON

### Fixed
- 4xx HTTP errors no longer trigger alerts in FastAPI, ASGI, and WSGI middlewares (only 5xx)

## [0.2.0] - 2026-03-13

### Added
- **Web frameworks**: Flask, Sanic, Litestar, aiohttp, generic ASGI, generic WSGI middlewares
- **Task queues**: Dramatiq, RQ (Redis Queue), Huey integrations
- **Scheduler**: APScheduler listener (v3 + v4)
- **Playwright**: sync/async context managers with auto-screenshot on failure
- **Playwright pytest plugin**: automatic screenshot + alert on test failure
- **`send_photo()`**: send screenshots/images via Telegram `sendPhoto` API
- Import-time dependency checks with clear install instructions for all integrations

## [0.1.2] - 2026-03-13

### Fixed
- Thread-safe config (`frozen` dataclass + `threading.Lock`)
- Thread-safe rate limiter with max entries cap (1024) to prevent memory leak
- Celery signals weak reference GC bug (moved handlers to module level)
- Traceback truncation by lines instead of bytes (prevents broken HTML tags)
- Django middleware now filters `Http404`, `PermissionDenied`, `SuspiciousOperation`

### Added
- Retry with backoff for Telegram API (2 retries on 5xx errors)
- `atexit` flush for pending daemon threads
- `py.typed` marker for type checker support
- Integration tests for FastAPI, Django, Celery

## [0.1.1] - 2026-03-13

### Added
- Django middleware integration (`WatcherrMiddleware` with `process_exception` hook)

## [0.1.0] - 2026-03-13

### Added
- Core: `send_alert()`, `send_warning()`, `send_info()`
- Logging handler (`WatcherrHandler`)
- FastAPI middleware
- Celery signals (task failure + retry)
- Rate limiter (dedup window)
- Configuration via code or environment variables
- Telegram bot for getting chat ID
