from __future__ import annotations

import traceback
from datetime import datetime, timezone

LEVEL_EMOJI = {
    "error": "\U0001f534",
    "warning": "\U0001f7e1",
    "info": "\U0001f535",
}


def format_message(
    level: str,
    message: str,
    service_name: str,
    environment: str,
    exc: BaseException | None = None,
    extra: dict | None = None,
) -> str:
    emoji = LEVEL_EMOJI.get(level, "\u2753")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    title = f"{emoji} <b>{level.upper()}</b> | <b>{service_name}</b> [{environment}]"

    parts = [title, "", message]

    if exc:
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        if len(tb) > 2000:
            tb = tb[:2000] + "\n... (truncated)"
        parts.append(f"\n<pre>{_escape_html(tb)}</pre>")

    if extra:
        lines = [f"  <b>{k}</b>: {_escape_html(str(v))}" for k, v in extra.items()]
        parts.append("\n" + "\n".join(lines))

    parts.append(f"\n<i>{now}</i>")

    return "\n".join(parts)


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
