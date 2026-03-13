import sys
from unittest.mock import MagicMock, patch

from watcherr import configure

# Mock rq if not installed
if "rq" not in sys.modules:
    sys.modules["rq"] = MagicMock()

from watcherr.integrations.rq_handler import watcherr_exception_handler


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


def _make_job(func_name="tasks.send_email", job_id="job-123", origin="default"):
    job = MagicMock()
    job.id = job_id
    job.func_name = func_name
    job.origin = origin
    return job


@patch("watcherr.integrations.rq_handler.send_alert")
def test_exception_handler_sends_alert(mock_send):
    _setup()
    job = _make_job()
    exc = ValueError("failed")

    result = watcherr_exception_handler(job, ValueError, exc, None)

    assert result is True
    mock_send.assert_called_once()
    assert "send_email" in mock_send.call_args[0][0]
    assert mock_send.call_args[1]["job_id"] == "job-123"
    assert mock_send.call_args[1]["queue"] == "default"


@patch("watcherr.integrations.rq_handler.send_alert")
def test_none_job_handled(mock_send):
    _setup()
    exc = RuntimeError("boom")

    result = watcherr_exception_handler(None, RuntimeError, exc, None)

    assert result is True
    mock_send.assert_called_once()
    assert "unknown" in mock_send.call_args[0][0]
