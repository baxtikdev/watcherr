from unittest.mock import MagicMock, patch

from watcherr.config import configure
from watcherr.sender import send_alert, send_info, send_warning


def _setup_config():
    configure(
        bot_token="123:TEST",
        chat_id="-999",
        service_name="test",
        environment="test",
        rate_limit_seconds=0,
    )


@patch("watcherr.sender._dispatch")
def test_send_alert_dispatches(mock_dispatch: MagicMock):
    _setup_config()
    send_alert("test error")
    mock_dispatch.assert_called_once()
    text = mock_dispatch.call_args[0][0]
    assert "ERROR" in text
    assert "test error" in text


@patch("watcherr.sender._dispatch")
def test_send_warning_dispatches(mock_dispatch: MagicMock):
    _setup_config()
    send_warning("test warning")
    mock_dispatch.assert_called_once()
    text = mock_dispatch.call_args[0][0]
    assert "WARNING" in text


@patch("watcherr.sender._dispatch")
def test_send_info_dispatches(mock_dispatch: MagicMock):
    _setup_config()
    send_info("deployed v1.2")
    mock_dispatch.assert_called_once()
    text = mock_dispatch.call_args[0][0]
    assert "INFO" in text


@patch("watcherr.sender._dispatch")
def test_disabled_config_skips(mock_dispatch: MagicMock):
    configure(bot_token="123:TEST", chat_id="-999", enabled=False)
    send_alert("should not send")
    mock_dispatch.assert_not_called()


@patch("watcherr.sender._dispatch")
def test_missing_token_skips(mock_dispatch: MagicMock):
    configure(bot_token="", chat_id="-999")
    send_alert("should not send")
    mock_dispatch.assert_not_called()
