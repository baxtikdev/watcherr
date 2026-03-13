from __future__ import annotations

try:
    import dramatiq  # noqa: F401
except ImportError:
    raise ImportError("Install watcherr[dramatiq]: pip install watcherr[dramatiq]") from None

from watcherr.sender import send_alert, send_warning


class WatcherrMiddleware(dramatiq.Middleware):
    """Dramatiq middleware that sends alerts on actor failures and retries.

    Usage:
        import dramatiq
        from watcherr.integrations.dramatiq_middleware import WatcherrMiddleware

        dramatiq.get_broker().add_middleware(WatcherrMiddleware())
    """

    def actor_failure(self, broker, message, *, exception):
        actor_name = message.actor_name
        send_alert(
            f"Dramatiq actor failed: <b>{actor_name}</b>",
            exc=exception,
            actor=actor_name,
            message_id=message.message_id,
            queue=message.queue_name,
        )

    def before_retry(self, broker, message, *, exception):
        actor_name = message.actor_name
        retries = message.options.get("retries", 0)
        send_warning(
            f"Dramatiq actor retrying: <b>{actor_name}</b>",
            exc=exception,
            actor=actor_name,
            message_id=message.message_id,
            retry=str(retries),
        )
