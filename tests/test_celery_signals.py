from unittest.mock import MagicMock, patch

from watcherr import configure


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


@patch("watcherr.integrations.celery_signals.send_alert")
def test_on_task_failure_sends_alert(mock_send):
    _setup()
    from watcherr.integrations.celery_signals import _on_task_failure

    sender = MagicMock()
    sender.name = "app.tasks.process_data"
    exc = ValueError("db connection failed")

    _on_task_failure(sender=sender, task_id="abc-123", exception=exc, traceback=None)

    mock_send.assert_called_once()
    assert "process_data" in mock_send.call_args[0][0]
    assert mock_send.call_args[1]["exc"] is exc
    assert mock_send.call_args[1]["task_id"] == "abc-123"


@patch("watcherr.integrations.celery_signals.send_warning")
def test_on_task_retry_sends_warning(mock_send):
    _setup()
    from watcherr.integrations.celery_signals import _on_task_retry

    sender = MagicMock()
    sender.name = "app.tasks.send_email"
    request = MagicMock()
    request.id = "def-456"

    _on_task_retry(sender=sender, request=request, reason="ConnectionError")

    mock_send.assert_called_once()
    assert "send_email" in mock_send.call_args[0][0]
    assert mock_send.call_args[1]["reason"] == "ConnectionError"


@patch("watcherr.integrations.celery_signals.send_alert")
def test_unknown_sender_handled(mock_send):
    _setup()
    from watcherr.integrations.celery_signals import _on_task_failure

    _on_task_failure(sender=None, task_id=None, exception=RuntimeError("boom"), traceback=None)

    mock_send.assert_called_once()
    assert "unknown" in mock_send.call_args[0][0]


def test_setup_connects_signals():
    from celery.signals import task_failure

    from watcherr.integrations.celery_signals import _on_task_failure, setup_celery_alerts

    setup_celery_alerts()

    failure_receivers = [r for r in task_failure.receivers if r[1]() is _on_task_failure or r[1] is _on_task_failure]
    assert len(failure_receivers) > 0
