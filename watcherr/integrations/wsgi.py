from __future__ import annotations

from watcherr.sender import send_alert


class WatcherrWSGIMiddleware:
    """Generic WSGI middleware — works with any WSGI framework.

    Usage:
        from watcherr.integrations.wsgi import WatcherrWSGIMiddleware

        app = WatcherrWSGIMiddleware(app)
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except Exception as exc:
            method = environ.get("REQUEST_METHOD", "UNKNOWN")
            path = environ.get("PATH_INFO", "/")
            client = environ.get("REMOTE_ADDR", "unknown")

            send_alert(
                f"Unhandled exception in {method} {path}",
                exc=exc,
                method=method,
                path=path,
                client=client,
            )
            raise
