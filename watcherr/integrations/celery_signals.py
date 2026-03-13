from __future__ import annotations

from watcherr.sender import send_alert, send_warning


def _on_task_failure(sender=None, task_id=None, exception=None, traceback=None, **kwargs):
    task_name = sender.name if sender else "unknown"
    send_alert(
        f"Celery task failed: <b>{task_name}</b>",
        exc=exception,
        task_id=task_id or "",
        task=task_name,
    )


def _on_task_retry(sender=None, request=None, reason=None, **kwargs):
    task_name = sender.name if sender else "unknown"
    send_warning(
        f"Celery task retrying: <b>{task_name}</b>",
        reason=str(reason) if reason else "",
        task_id=request.id if request else "",
        task=task_name,
    )


def setup_celery_alerts() -> None:
    from celery.signals import task_failure, task_retry

    task_failure.connect(_on_task_failure)
    task_retry.connect(_on_task_retry)
