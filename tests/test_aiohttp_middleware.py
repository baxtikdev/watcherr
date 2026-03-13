import sys
from unittest.mock import AsyncMock, MagicMock, patch

from watcherr import configure

# Mock aiohttp if not installed
if "aiohttp" not in sys.modules:
    aiohttp_mock = MagicMock()

    def _middleware_decorator(fn):
        return fn

    aiohttp_mock.web.middleware = _middleware_decorator
    aiohttp_mock.web.HTTPException = type("HTTPException", (Exception,), {})
    sys.modules["aiohttp"] = aiohttp_mock
    sys.modules["aiohttp.web"] = aiohttp_mock.web

from watcherr.integrations.aiohttp_middleware import watcherr_middleware


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


def _make_request(method="GET", path="/test"):
    request = MagicMock()
    request.method = method
    request.path = path
    request.remote = "127.0.0.1"
    return request


@patch("watcherr.integrations.aiohttp_middleware.send_alert")
async def test_successful_request_no_alert(mock_send):
    _setup()
    mw = watcherr_middleware()
    handler = AsyncMock(return_value=MagicMock())
    request = _make_request()

    await mw(request, handler)

    handler.assert_awaited_once_with(request)
    mock_send.assert_not_called()


@patch("watcherr.integrations.aiohttp_middleware.send_alert")
async def test_exception_sends_alert(mock_send):
    _setup()
    mw = watcherr_middleware()
    handler = AsyncMock(side_effect=RuntimeError("boom"))
    request = _make_request(method="POST", path="/api")

    try:
        await mw(request, handler)
    except RuntimeError:
        pass

    mock_send.assert_called_once()
    assert "POST" in mock_send.call_args[0][0]
    assert "/api" in mock_send.call_args[0][0]
