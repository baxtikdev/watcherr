import sys
from unittest.mock import MagicMock, patch

from watcherr import configure

# Mock apscheduler if not installed
if "apscheduler" not in sys.modules:
    apscheduler_mock = MagicMock()
    apscheduler_mock.events = MagicMock()
    apscheduler_mock.events.EVENT_JOB_ERROR = 1 << 10
    apscheduler_mock.events.EVENT_JOB_MISSED = 1 << 11
    sys.modules["apscheduler"] = apscheduler_mock
    sys.modules["apscheduler.events"] = apscheduler_mock.events

from watcherr.integrations.apscheduler_listener import setup_apscheduler_alerts


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


@patch("watcherr.integrations.apscheduler_listener.send_alert")
def test_job_error_sends_alert(mock_send):
    _setup()
    scheduler = MagicMock()
    setup_apscheduler_alerts(scheduler)

    # Get the registered error listener
    calls = scheduler.add_listener.call_args_list
    assert len(calls) >= 1

    error_handler = calls[0][0][0]

    event = MagicMock()
    event.job_id = "daily-cleanup"
    event.exception = ValueError("db down")
    event.scheduled_run_time = "2026-03-13 00:00:00"

    error_handler(event)

    mock_send.assert_called_once()
    assert "daily-cleanup" in mock_send.call_args[0][0]
    assert mock_send.call_args[1]["exc"] is event.exception


@patch("watcherr.integrations.apscheduler_listener.send_alert")
def test_job_missed_sends_alert(mock_send):
    _setup()
    scheduler = MagicMock()
    setup_apscheduler_alerts(scheduler)

    calls = scheduler.add_listener.call_args_list
    assert len(calls) >= 2

    missed_handler = calls[1][0][0]

    event = MagicMock()
    event.job_id = "weekly-report"
    event.scheduled_run_time = "2026-03-13 00:00:00"

    missed_handler(event)

    mock_send.assert_called_once()
    assert "weekly-report" in mock_send.call_args[0][0]
    assert "missed" in mock_send.call_args[0][0].lower()


def test_setup_registers_two_listeners():
    _setup()
    scheduler = MagicMock()
    setup_apscheduler_alerts(scheduler)

    assert scheduler.add_listener.call_count == 2
