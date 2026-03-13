import sys
from unittest.mock import MagicMock, patch

from watcherr import configure

# Mock dramatiq if not installed
if "dramatiq" not in sys.modules:
    dramatiq_mock = MagicMock()
    dramatiq_mock.Middleware = type("Middleware", (), {})
    sys.modules["dramatiq"] = dramatiq_mock

from watcherr.integrations.dramatiq_middleware import WatcherrMiddleware


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


def _make_message(actor_name="tasks.send_email", message_id="abc-123", queue="default"):
    msg = MagicMock()
    msg.actor_name = actor_name
    msg.message_id = message_id
    msg.queue_name = queue
    msg.options = {"retries": 3}
    return msg


@patch("watcherr.integrations.dramatiq_middleware.send_alert")
def test_actor_failure_sends_alert(mock_send):
    _setup()
    mw = WatcherrMiddleware()
    msg = _make_message()
    exc = ValueError("db error")

    mw.actor_failure(MagicMock(), msg, exception=exc)

    mock_send.assert_called_once()
    assert "send_email" in mock_send.call_args[0][0]
    assert mock_send.call_args[1]["exc"] is exc


@patch("watcherr.integrations.dramatiq_middleware.send_warning")
def test_before_retry_sends_warning(mock_send):
    _setup()
    mw = WatcherrMiddleware()
    msg = _make_message(actor_name="tasks.process")
    exc = ConnectionError("timeout")

    mw.before_retry(MagicMock(), msg, exception=exc)

    mock_send.assert_called_once()
    assert "process" in mock_send.call_args[0][0]
