from __future__ import annotations

import logging

from watcherr.sender import send_alert, send_warning


class WatcherrHandler(logging.Handler):
    def __init__(self, level: int = logging.ERROR):
        super().__init__(level)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record) if self.formatter else record.getMessage()
            extra = {
                "logger": record.name,
                "module": record.module,
            }

            if record.funcName:
                extra["function"] = record.funcName

            exc = record.exc_info[1] if record.exc_info and record.exc_info[1] else None

            if record.levelno >= logging.ERROR:
                send_alert(message, exc=exc, **extra)
            elif record.levelno >= logging.WARNING:
                send_warning(message, exc=exc, **extra)
        except Exception:
            self.handleError(record)
