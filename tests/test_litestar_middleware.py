import sys
from unittest.mock import MagicMock, patch

from watcherr import configure

# Mock litestar if not installed
if "litestar" not in sys.modules:
    litestar_mock = MagicMock()
    litestar_mock.Request = MagicMock
    litestar_mock.Response = MagicMock

    class FakeHTTPException(Exception):
        def __init__(self, status_code=500, detail="error"):
            self.status_code = status_code
            self.detail = detail

    litestar_mock.exceptions.HTTPException = FakeHTTPException
    sys.modules["litestar"] = litestar_mock
    sys.modules["litestar.exceptions"] = litestar_mock.exceptions

from watcherr.integrations.litestar_middleware import create_exception_handler


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


def _make_request(method="GET", path="/test"):
    request = MagicMock()
    request.method = method
    request.url.path = path
    request.client.host = "127.0.0.1"
    return request


@patch("watcherr.integrations.litestar_middleware.send_alert")
async def test_unhandled_exception_sends_alert(mock_send):
    _setup()
    handler = create_exception_handler()
    request = _make_request(method="POST", path="/api")
    exc = RuntimeError("boom")

    result = await handler(request, exc)

    mock_send.assert_called_once()
    assert "POST" in mock_send.call_args[0][0]
    assert "/api" in mock_send.call_args[0][0]
    assert result is not None


@patch("watcherr.integrations.litestar_middleware.send_alert")
async def test_http_exception_no_alert(mock_send):
    _setup()
    from litestar.exceptions import HTTPException

    handler = create_exception_handler()
    request = _make_request()
    exc = HTTPException(status_code=404, detail="Not found")

    await handler(request, exc)

    mock_send.assert_not_called()
