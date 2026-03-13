import logging
from unittest.mock import patch

from watcherr.config import configure
from watcherr.logging_handler import WatcherrHandler


def _setup():
    configure(
        bot_token="123:TEST",
        chat_id="-999",
        service_name="test",
        rate_limit_seconds=0,
    )


@patch("watcherr.logging_handler.send_alert")
def test_error_log_sends_alert(mock_send):
    _setup()
    logger = logging.getLogger("test.handler.error")
    logger.addHandler(WatcherrHandler(level=logging.ERROR))
    logger.setLevel(logging.ERROR)

    logger.error("something failed")

    mock_send.assert_called_once()
    assert "something failed" in mock_send.call_args[0][0]


@patch("watcherr.logging_handler.send_warning")
def test_warning_log_sends_warning(mock_send):
    _setup()
    handler = WatcherrHandler(level=logging.WARNING)
    logger = logging.getLogger("test.handler.warning")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    logger.warning("slow response")

    mock_send.assert_called_once()


@patch("watcherr.logging_handler.send_alert")
def test_below_level_ignored(mock_send):
    _setup()
    handler = WatcherrHandler(level=logging.ERROR)
    logger = logging.getLogger("test.handler.below")
    logger.handlers = [handler]
    logger.setLevel(logging.DEBUG)

    logger.info("not important")

    mock_send.assert_not_called()
