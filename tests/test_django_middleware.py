from unittest.mock import MagicMock, patch

from watcherr import configure
from watcherr.integrations.django_middleware import WatcherrMiddleware


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


def _make_request(method="GET", path="/test"):
    request = MagicMock()
    request.method = method
    request.path = path
    request.META = {"REMOTE_ADDR": "127.0.0.1"}
    return request


@patch("watcherr.integrations.django_middleware.send_alert")
def test_unhandled_exception_sends_alert(mock_send):
    _setup()
    mw = WatcherrMiddleware(get_response=MagicMock())
    request = _make_request()
    exc = RuntimeError("something broke")

    mw.process_exception(request, exc)

    mock_send.assert_called_once()
    assert "GET" in mock_send.call_args[0][0]
    assert "/test" in mock_send.call_args[0][0]


@patch("watcherr.integrations.django_middleware.send_alert")
def test_normal_request_no_alert(mock_send):
    _setup()
    response = MagicMock()
    get_response = MagicMock(return_value=response)
    mw = WatcherrMiddleware(get_response=get_response)
    request = _make_request()

    result = mw(request)

    assert result == response
    mock_send.assert_not_called()


@patch("watcherr.integrations.django_middleware.send_alert")
def test_alert_contains_client_ip(mock_send):
    _setup()
    mw = WatcherrMiddleware(get_response=MagicMock())
    request = _make_request(method="POST", path="/api/data")

    mw.process_exception(request, ValueError("bad"))

    mock_send.assert_called_once()
    kwargs = mock_send.call_args[1]
    assert kwargs["client"] == "127.0.0.1"
    assert kwargs["method"] == "POST"
    assert kwargs["path"] == "/api/data"
