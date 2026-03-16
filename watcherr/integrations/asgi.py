from __future__ import annotations

from watcherr.sender import send_alert


class WatcherrASGIMiddleware:
    """Generic ASGI middleware — works with any ASGI framework.

    Usage:
        from watcherr.integrations.asgi import WatcherrASGIMiddleware

        app = WatcherrASGIMiddleware(app)
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
            if isinstance(status, int) and 400 <= status < 500:
                raise

            method = scope.get("method", "UNKNOWN")
            path = scope.get("path", "/")
            client = scope.get("client")
            client_host = client[0] if client else "unknown"

            send_alert(
                f"Unhandled exception in {method} {path}",
                exc=exc,
                method=method,
                path=path,
                client=client_host,
            )
            raise
