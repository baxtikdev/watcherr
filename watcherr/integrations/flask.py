from __future__ import annotations

try:
    from werkzeug.exceptions import HTTPException  # noqa: F401
except ImportError:
    raise ImportError("Install watcherr[flask]: pip install watcherr[flask]") from None

from watcherr.sender import send_alert


def init_app(app) -> None:
    """Register watcherr error handler on a Flask app.

    Usage:
        from watcherr.integrations.flask import init_app
        init_app(app)
    """

    @app.errorhandler(Exception)
    def _handle_exception(exc):
        if isinstance(exc, HTTPException):
            return exc

        from flask import request

        send_alert(
            f"Unhandled exception in {request.method} {request.path}",
            exc=exc,
            method=request.method,
            path=request.path,
            client=request.remote_addr or "unknown",
        )
        raise exc
