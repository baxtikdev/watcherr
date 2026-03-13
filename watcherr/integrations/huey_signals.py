from __future__ import annotations

try:
    import huey  # noqa: F401
except ImportError:
    raise ImportError("Install watcherr[huey]: pip install watcherr[huey]") from None

from watcherr.sender import send_alert, send_warning


def setup_huey_alerts(huey) -> None:
    """Register watcherr error handlers on a Huey instance.

    Usage:
        from huey import RedisHuey
        from watcherr.integrations.huey_signals import setup_huey_alerts

        huey = RedisHuey("my-app")
        setup_huey_alerts(huey)
    """

    @huey.on_error()
    def _on_error(task, exc):
        task_name = task.name if task else "unknown"
        send_alert(
            f"Huey task failed: <b>{task_name}</b>",
            exc=exc,
            task=task_name,
            task_id=task.id if task else "",
        )

    @huey.pre_execute()
    def _on_retry(task):
        retries = getattr(task, "retries", 0)
        if retries and task.retries_remaining and task.retries_remaining < retries:
            send_warning(
                f"Huey task retrying: <b>{task.name}</b>",
                task=task.name,
                task_id=task.id,
                retries_remaining=str(task.retries_remaining),
            )
