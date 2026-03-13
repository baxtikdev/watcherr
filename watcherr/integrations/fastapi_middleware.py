from __future__ import annotations

from watcherr.sender import send_alert


def WatcherrMiddleware(app):
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response

    class _Middleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next) -> Response:
            try:
                return await call_next(request)
            except Exception as exc:
                send_alert(
                    f"Unhandled exception in {request.method} {request.url.path}",
                    exc=exc,
                    method=request.method,
                    path=request.url.path,
                    client=request.client.host if request.client else "unknown",
                )
                raise

    return _Middleware(app)
