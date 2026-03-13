from __future__ import annotations

try:
    from litestar import Request, Response  # noqa: F401
    from litestar.exceptions import HTTPException  # noqa: F401
except ImportError:
    raise ImportError("Install watcherr[litestar]: pip install watcherr[litestar]") from None

from watcherr.sender import send_alert


def create_exception_handler():
    """Create a Litestar exception handler for watcherr.

    Usage:
        from litestar import Litestar
        from watcherr.integrations.litestar_middleware import create_exception_handler

        app = Litestar(
            exception_handlers={Exception: create_exception_handler()},
        )
    """

    async def _handler(request: Request, exc: Exception) -> Response:
        if isinstance(exc, HTTPException):
            return Response(
                content={"detail": exc.detail},
                status_code=exc.status_code,
            )

        send_alert(
            f"Unhandled exception in {request.method} {request.url.path}",
            exc=exc,
            method=request.method,
            path=str(request.url.path),
            client=request.client.host if request.client else "unknown",
        )
        return Response(content={"detail": "Internal Server Error"}, status_code=500)

    return _handler
