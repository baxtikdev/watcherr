from __future__ import annotations

try:
    from aiohttp.web import HTTPException, middleware  # noqa: F401
except ImportError:
    raise ImportError("Install watcherr[aiohttp]: pip install watcherr[aiohttp]") from None

from watcherr.sender import send_alert


def watcherr_middleware():
    """Create an aiohttp middleware that sends alerts on unhandled exceptions.

    Usage:
        from aiohttp import web
        from watcherr.integrations.aiohttp_middleware import watcherr_middleware

        app = web.Application(middlewares=[watcherr_middleware()])
    """

    @middleware
    async def _middleware(request, handler):
        try:
            return await handler(request)
        except HTTPException:
            raise
        except Exception as exc:
            send_alert(
                f"Unhandled exception in {request.method} {request.path}",
                exc=exc,
                method=request.method,
                path=request.path,
                client=request.remote or "unknown",
            )
            raise

    return _middleware
