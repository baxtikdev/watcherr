from __future__ import annotations

from watcherr.sender import send_alert


def watcherr_exception_handler(job, exc_type, exc_value, traceback):
    """RQ exception handler — sends alert on job failure.

    Usage:
        from rq import Worker
        from watcherr.integrations.rq_handler import watcherr_exception_handler

        worker = Worker(queues, exception_handlers=[watcherr_exception_handler])

    Or in rq worker config (worker_settings.py):
        EXCEPTION_HANDLERS = ["watcherr.integrations.rq_handler.watcherr_exception_handler"]
    """
    job_id = job.id if job else "unknown"
    func_name = job.func_name if job else "unknown"
    queue_name = job.origin if job else "unknown"

    send_alert(
        f"RQ job failed: <b>{func_name}</b>",
        exc=exc_value,
        job_id=job_id,
        function=func_name,
        queue=queue_name,
    )
    return True
