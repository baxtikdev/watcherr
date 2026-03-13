from __future__ import annotations

try:
    import apscheduler  # noqa: F401
except ImportError:
    raise ImportError("Install watcherr[apscheduler]: pip install watcherr[apscheduler]") from None

from watcherr.sender import send_alert


def setup_apscheduler_alerts(scheduler) -> None:
    """Register watcherr error listener on an APScheduler scheduler.

    Works with both APScheduler 3.x and 4.x.

    Usage (v3):
        from apscheduler.schedulers.background import BackgroundScheduler
        from watcherr.integrations.apscheduler_listener import setup_apscheduler_alerts

        scheduler = BackgroundScheduler()
        setup_apscheduler_alerts(scheduler)

    Usage (v4):
        from apscheduler import Scheduler
        from watcherr.integrations.apscheduler_listener import setup_apscheduler_alerts

        scheduler = Scheduler()
        setup_apscheduler_alerts(scheduler)
    """
    try:
        _setup_v3(scheduler)
    except (ImportError, AttributeError):
        try:
            _setup_v4(scheduler)
        except (ImportError, AttributeError):
            raise RuntimeError("watcherr: unsupported APScheduler version")


def _setup_v3(scheduler) -> None:
    from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED

    def _on_job_error(event):
        job_id = event.job_id
        exc = event.exception

        send_alert(
            f"APScheduler job failed: <b>{job_id}</b>",
            exc=exc,
            job_id=job_id,
            scheduled_time=str(event.scheduled_run_time) if event.scheduled_run_time else "",
        )

    def _on_job_missed(event):
        send_alert(
            f"APScheduler job missed: <b>{event.job_id}</b>",
            job_id=event.job_id,
            scheduled_time=str(event.scheduled_run_time) if event.scheduled_run_time else "",
        )

    scheduler.add_listener(_on_job_error, EVENT_JOB_ERROR)
    scheduler.add_listener(_on_job_missed, EVENT_JOB_MISSED)


def _setup_v4(scheduler) -> None:
    from apscheduler import JobOutcome

    original_handler = getattr(scheduler, "_job_result_callback", None)

    def _on_result(event):
        if original_handler:
            original_handler(event)
        if event.outcome == JobOutcome.error:
            send_alert(
                f"APScheduler job failed: <b>{event.job_id}</b>",
                exc=event.exception if hasattr(event, "exception") else None,
                job_id=str(event.job_id),
            )

    scheduler.subscribe(_on_result)
