from __future__ import annotations

from watcherr.sender import send_alert, send_warning


class WatcherrMiddleware:
    """Dramatiq middleware that sends alerts on actor failures and retries.

    Usage:
        import dramatiq
        from watcherr.integrations.dramatiq_middleware import WatcherrMiddleware

        dramatiq.get_broker().add_middleware(WatcherrMiddleware())
    """

    class _Impl:
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

    def __new__(cls):
        from dramatiq import Middleware

        attrs = {
            "actor_failure": cls._Impl.actor_failure,
            "before_retry": cls._Impl.before_retry,
        }
        klass = type("WatcherrMiddleware", (Middleware,), attrs)
        return klass()
