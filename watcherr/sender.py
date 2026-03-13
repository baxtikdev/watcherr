from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any

import httpx

from watcherr.config import WatcherrConfig, get_config
from watcherr.formatter import format_message
from watcherr.rate_limiter import get_rate_limiter

logger = logging.getLogger("watcherr")

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def _send_sync(text: str, config: WatcherrConfig) -> bool:
    url = TELEGRAM_API.format(token=config.bot_token)
    try:
        resp = httpx.post(url, json={"chat_id": config.chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
        if not resp.is_success:
            logger.warning("watcherr: telegram %s: %s", resp.status_code, resp.text[:200])
        return resp.is_success
    except Exception:
        logger.debug("watcherr: send failed", exc_info=True)
        return False


async def _send_async(text: str, config: WatcherrConfig) -> bool:
    url = TELEGRAM_API.format(token=config.bot_token)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url, json={"chat_id": config.chat_id, "text": text, "parse_mode": "HTML"}, timeout=10
            )
            if not resp.is_success:
                logger.warning("watcherr: telegram %s: %s", resp.status_code, resp.text[:200])
            return resp.is_success
    except Exception:
        logger.debug("watcherr: send failed", exc_info=True)
        return False


def _dispatch(text: str) -> None:
    config = get_config()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(_send_async(text, config))
    else:
        threading.Thread(target=_send_sync, args=(text, config), daemon=True).start()


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
