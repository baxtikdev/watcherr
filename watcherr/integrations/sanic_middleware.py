from __future__ import annotations

try:
    from sanic.exceptions import SanicException  # noqa: F401
except ImportError:
    raise ImportError("Install watcherr[sanic]: pip install watcherr[sanic]") from None

from watcherr.sender import send_alert


def init_app(app) -> None:
    """Register watcherr error handler on a Sanic app.

    Usage:
        from watcherr.integrations.sanic_middleware import init_app
        init_app(app)
    """

    @app.exception(Exception)
    async def _handle_exception(request, exc):
        if isinstance(exc, SanicException):
            raise exc

        send_alert(
            f"Unhandled exception in {request.method} {request.path}",
            exc=exc,
            method=request.method,
            path=request.path,
            client=request.remote_addr or request.ip or "unknown",
        )
        raise exc
