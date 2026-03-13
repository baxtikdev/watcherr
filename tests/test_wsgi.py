from unittest.mock import MagicMock, patch

from watcherr import configure
from watcherr.integrations.wsgi import WatcherrWSGIMiddleware


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


def _ok_app(environ, start_response):
    start_response("200 OK", [])
    return [b"ok"]


def _fail_app(environ, start_response):
    raise RuntimeError("boom")


def _make_environ(method="GET", path="/test"):
    return {"REQUEST_METHOD": method, "PATH_INFO": path, "REMOTE_ADDR": "127.0.0.1"}


@patch("watcherr.integrations.wsgi.send_alert")
def test_successful_request_no_alert(mock_send):
    _setup()
    app = WatcherrWSGIMiddleware(_ok_app)
    result = app(_make_environ(), MagicMock())
    assert result == [b"ok"]
    mock_send.assert_not_called()


@patch("watcherr.integrations.wsgi.send_alert")
def test_exception_sends_alert(mock_send):
    _setup()
    app = WatcherrWSGIMiddleware(_fail_app)
    try:
        app(_make_environ(method="POST", path="/api"), MagicMock())
    except RuntimeError:
        pass
    mock_send.assert_called_once()
    assert "POST" in mock_send.call_args[0][0]
    assert "/api" in mock_send.call_args[0][0]
    assert mock_send.call_args[1]["client"] == "127.0.0.1"
