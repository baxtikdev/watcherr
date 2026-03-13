from __future__ import annotations

import atexit
import asyncio
import logging
import threading
import time
from typing import Any

import httpx

from watcherr.config import WatcherrConfig, get_config
from watcherr.formatter import format_message
from watcherr.rate_limiter import get_rate_limiter

logger = logging.getLogger("watcherr")

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"

_MAX_RETRIES = 2
_RETRY_DELAY = 0.5

_pending_threads: list[threading.Thread] = []
_pending_lock = threading.Lock()


def _send_sync(text: str, config: WatcherrConfig) -> bool:
    url = TELEGRAM_API.format(token=config.bot_token)
    for attempt in range(_MAX_RETRIES + 1):
        try:
            resp = httpx.post(url, json={"chat_id": config.chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
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


async def _send_async(text: str, config: WatcherrConfig) -> bool:
    url = TELEGRAM_API.format(token=config.bot_token)
    for attempt in range(_MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url, json={"chat_id": config.chat_id, "text": text, "parse_mode": "HTML"}, timeout=10
                )
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


def _tracked_send(text: str, config: WatcherrConfig) -> None:
    try:
        _send_sync(text, config)
    finally:
        thread = threading.current_thread()
        with _pending_lock:
            try:
                _pending_threads.remove(thread)
            except ValueError:
                pass


def _dispatch(text: str) -> None:
    config = get_config()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(_send_async(text, config))
    else:
        t = threading.Thread(target=_tracked_send, args=(text, config), daemon=True)
        with _pending_lock:
            _pending_threads.append(t)
        t.start()


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
