from __future__ import annotations

import asyncio
import atexit
import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable

import httpx

from watcherr.config import WatcherrConfig, get_config
from watcherr.formatter import format_message
from watcherr.rate_limiter import get_rate_limiter

logger = logging.getLogger("watcherr")

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

_MAX_RETRIES = 2
_RETRY_DELAY = 0.5

_pending_threads: list[threading.Thread] = []
_pending_lock = threading.Lock()


def _build_url(config: WatcherrConfig, method: str) -> str:
    return TELEGRAM_API.format(token=config.bot_token, method=method)


def _retry_sync(fn: Callable[[], httpx.Response]) -> bool:
    for attempt in range(_MAX_RETRIES + 1):
        try:
            resp = fn()
            if resp.is_success:
                return True
            logger.warning("watcherr: telegram %s: %s", resp.status_code, resp.text[:200])
            if resp.status_code < 500:
                return False
        except Exception:
            logger.debug("watcherr: send failed (attempt %d)", attempt + 1, exc_info=True)
        if attempt < _MAX_RETRIES:
            time.sleep(_RETRY_DELAY * (attempt + 1))
    return False


async def _retry_async(fn: Callable[[], Any]) -> bool:
    for attempt in range(_MAX_RETRIES + 1):
        try:
            resp = await fn()
            if resp.is_success:
                return True
            logger.warning("watcherr: telegram %s: %s", resp.status_code, resp.text[:200])
            if resp.status_code < 500:
                return False
        except Exception:
            logger.debug("watcherr: send failed (attempt %d)", attempt + 1, exc_info=True)
        if attempt < _MAX_RETRIES:
            await asyncio.sleep(_RETRY_DELAY * (attempt + 1))
    return False


def _send_message_sync(text: str, config: WatcherrConfig) -> bool:
    url = _build_url(config, "sendMessage")
    return _retry_sync(
        lambda: httpx.post(url, json={"chat_id": config.chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
    )


async def _send_message_async(text: str, config: WatcherrConfig) -> bool:
    url = _build_url(config, "sendMessage")

    async def _call():
        async with httpx.AsyncClient() as client:
            return await client.post(
                url, json={"chat_id": config.chat_id, "text": text, "parse_mode": "HTML"}, timeout=10
            )

    return await _retry_async(_call)


def _send_photo_sync(photo: bytes, caption: str, filename: str, config: WatcherrConfig) -> bool:
    url = _build_url(config, "sendPhoto")
    return _retry_sync(
        lambda: httpx.post(
            url,
            data={"chat_id": config.chat_id, "caption": caption[:1024], "parse_mode": "HTML"},
            files={"photo": (filename, photo, "image/png")},
            timeout=30,
        )
    )


async def _send_photo_async(photo: bytes, caption: str, filename: str, config: WatcherrConfig) -> bool:
    url = _build_url(config, "sendPhoto")

    async def _call():
        async with httpx.AsyncClient() as client:
            return await client.post(
                url,
                data={"chat_id": config.chat_id, "caption": caption[:1024], "parse_mode": "HTML"},
                files={"photo": (filename, photo, "image/png")},
                timeout=30,
            )

    return await _retry_async(_call)


# --- dispatch ---


def _tracked_call(fn: Callable, *args: Any) -> None:
    try:
        fn(*args)
    finally:
        thread = threading.current_thread()
        with _pending_lock:
            try:
                _pending_threads.remove(thread)
            except ValueError:
                pass


def _dispatch_any(sync_fn: Callable, async_fn: Callable, *args: Any) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(async_fn(*args))
    else:
        t = threading.Thread(target=_tracked_call, args=(sync_fn, *args), daemon=True)
        with _pending_lock:
            _pending_threads.append(t)
        t.start()


def _dispatch(text: str) -> None:
    config = get_config()
    _dispatch_any(_send_message_sync, _send_message_async, text, config)


def _dispatch_photo(photo: bytes, caption: str, filename: str) -> None:
    config = get_config()
    _dispatch_any(_send_photo_sync, _send_photo_async, photo, caption, filename, config)


def _flush_pending(timeout: float = 5.0) -> None:
    with _pending_lock:
        threads = list(_pending_threads)
    deadline = time.monotonic() + timeout
    for t in threads:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        t.join(timeout=remaining)


atexit.register(_flush_pending)


# --- public API ---


def _send(level: str, message: str, exc: BaseException | None = None, extra: dict | None = None) -> None:
    config = get_config()
    if not config.enabled or not config.bot_token or not config.chat_id:
        return

    text = format_message(
        level=level,
        message=message,
        service_name=config.service_name,
        environment=config.environment,
        exc=exc,
        extra=extra,
    )

    limiter = get_rate_limiter(config.rate_limit_seconds)
    if not limiter.should_send(text):
        return

    _dispatch(text)


def send_alert(message: str, exc: BaseException | None = None, **extra: Any) -> None:
    _send("error", message, exc=exc, extra=extra or None)


def send_warning(message: str, exc: BaseException | None = None, **extra: Any) -> None:
    _send("warning", message, exc=exc, extra=extra or None)


def send_info(message: str, **extra: Any) -> None:
    _send("info", message, extra=extra or None)


def send_photo(
    photo: bytes | str | Path,
    caption: str = "",
    filename: str = "screenshot.png",
    exc: BaseException | None = None,
) -> None:
    config = get_config()
    if not config.enabled or not config.bot_token or not config.chat_id:
        return

    if isinstance(photo, (str, Path)):
        path = Path(photo)
        if not path.exists():
            logger.warning("watcherr: photo file not found: %s", path)
            return
        photo = path.read_bytes()
        filename = filename or path.name

    if exc:
        tb_line = f"{type(exc).__name__}: {exc}"
        if caption:
            caption = f"{caption}\n\n<pre>{tb_line}</pre>"
        else:
            caption = f"<pre>{tb_line}</pre>"

    _dispatch_photo(photo, caption, filename)
