from __future__ import annotations

from watcherr.sender import send_alert

_IGNORED_EXCEPTIONS: tuple[type, ...] | None = None


def _get_ignored_exceptions() -> tuple[type, ...]:
    global _IGNORED_EXCEPTIONS
    if _IGNORED_EXCEPTIONS is None:
        ignored: list[type] = []
        try:
            from django.http import Http404

            ignored.append(Http404)
        except ImportError:
            pass
        try:
            from django.core.exceptions import PermissionDenied, SuspiciousOperation

            ignored.extend([PermissionDenied, SuspiciousOperation])
        except ImportError:
            pass
        _IGNORED_EXCEPTIONS = tuple(ignored)
    return _IGNORED_EXCEPTIONS


class WatcherrMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        ignored = _get_ignored_exceptions()
        if ignored and isinstance(exception, ignored):
            return None

        send_alert(
            f"Unhandled exception in {request.method} {request.path}",
            exc=exception,
            method=request.method,
            path=request.path,
            client=request.META.get("REMOTE_ADDR", "unknown"),
        )
        return None
