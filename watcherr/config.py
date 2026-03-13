from __future__ import annotations

import os
import threading
from dataclasses import dataclass

_lock = threading.Lock()
_config: WatcherrConfig | None = None


@dataclass(frozen=True)
class WatcherrConfig:
    bot_token: str = ""
    chat_id: str = ""
    service_name: str = "app"
    environment: str = "production"
    rate_limit_seconds: int = 60
    enabled: bool = True


def configure(
    bot_token: str | None = None,
    chat_id: str | None = None,
    service_name: str | None = None,
    environment: str | None = None,
    rate_limit_seconds: int | None = None,
    enabled: bool | None = None,
) -> WatcherrConfig:
    global _config

    config = WatcherrConfig(
        bot_token=bot_token or os.getenv("WATCHERR_BOT_TOKEN", ""),
        chat_id=chat_id or os.getenv("WATCHERR_CHAT_ID", ""),
        service_name=service_name or os.getenv("WATCHERR_SERVICE_NAME", "app"),
        environment=environment or os.getenv("WATCHERR_ENVIRONMENT", "production"),
        rate_limit_seconds=(
            rate_limit_seconds if rate_limit_seconds is not None else int(os.getenv("WATCHERR_RATE_LIMIT", "60"))
        ),
        enabled=enabled if enabled is not None else os.getenv("WATCHERR_ENABLED", "true").lower() == "true",
    )

    with _lock:
        _config = config

    return config


def get_config() -> WatcherrConfig:
    global _config
    with _lock:
        if _config is None:
            _config = configure()
        return _config
