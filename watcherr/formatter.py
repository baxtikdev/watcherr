from __future__ import annotations

import traceback
from datetime import datetime, timezone

LEVEL_EMOJI = {
    "error": "\U0001f534",
    "warning": "\U0001f7e1",
    "info": "\U0001f535",
}

_MAX_TB_LINES = 50
_MAX_TB_CHARS = 2000


def _detect_language(text: str) -> str:
    if "Traceback (most recent call last)" in text or 'File "' in text:
        return "python"
    if "\tat " in text and ("Exception" in text or "Error" in text):
        return "java"
    if "at Object." in text or "at Module." in text or "at node:" in text:
        return "javascript"
    if "goroutine " in text or "panic:" in text:
        return "go"
    if "RuntimeError" in text or "NoMethodError" in text or ".rb:" in text:
        return "ruby"
    stripped = text.strip()
    if stripped.startswith(("{", "[")):
        return "json"
    return "python"


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
        tb = _truncate_traceback(exc)
        lang = _detect_language(tb)
        parts.append(f'\n<pre><code class="language-{lang}">{_escape_html(tb)}</code></pre>')

    if extra:
        lines = [f"  <b>{k}</b>: {_escape_html(str(v))}" for k, v in extra.items()]
        parts.append("\n" + "\n".join(lines))

    parts.append(f"\n<i>{now}</i>")

    return "\n".join(parts)


def _truncate_traceback(exc: BaseException) -> str:
    lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    tb_lines = "".join(lines).splitlines()

    if len(tb_lines) > _MAX_TB_LINES:
        tb_lines = tb_lines[:_MAX_TB_LINES]
        tb_lines.append(f"... ({len(tb_lines)} lines truncated)")

    result = "\n".join(tb_lines)
    if len(result) > _MAX_TB_CHARS:
        result = result[:_MAX_TB_CHARS].rsplit("\n", 1)[0]
        result += "\n... (truncated)"

    return result


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
