import sys
from unittest.mock import MagicMock, patch

from watcherr import configure

# Mock huey if not installed
if "huey" not in sys.modules:
    sys.modules["huey"] = MagicMock()

from watcherr.integrations.huey_signals import setup_huey_alerts


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


@patch("watcherr.integrations.huey_signals.send_alert")
def test_on_error_sends_alert(mock_send):
    _setup()
    huey = MagicMock()

    # Make decorators capture their functions
    captured = {}
    huey.on_error.return_value = lambda fn: captured.update(error=fn) or fn
    huey.pre_execute.return_value = lambda fn: captured.update(pre=fn) or fn

    setup_huey_alerts(huey)

    task = MagicMock()
    task.name = "tasks.process_data"
    task.id = "task-789"
    exc = ValueError("failed")

    captured["error"](task, exc)

    mock_send.assert_called_once()
    assert "process_data" in mock_send.call_args[0][0]
    assert mock_send.call_args[1]["exc"] is exc


def test_setup_registers_handlers():
    _setup()
    huey = MagicMock()
    setup_huey_alerts(huey)

    huey.on_error.assert_called_once()
    huey.pre_execute.assert_called_once()
