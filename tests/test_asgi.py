from unittest.mock import patch

from watcherr import configure
from watcherr.integrations.asgi import WatcherrASGIMiddleware


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


async def _ok_app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok"})


async def _fail_app(scope, receive, send):
    raise RuntimeError("boom")


@patch("watcherr.integrations.asgi.send_alert")
async def test_successful_request_no_alert(mock_send):
    _setup()
    app = WatcherrASGIMiddleware(_ok_app)
    scope = {"type": "http", "method": "GET", "path": "/ok", "client": ("127.0.0.1", 8000)}

    async def noop(msg):
        pass

    await app(scope, None, noop)
    mock_send.assert_not_called()


@patch("watcherr.integrations.asgi.send_alert")
async def test_exception_sends_alert(mock_send):
    _setup()
    app = WatcherrASGIMiddleware(_fail_app)
    scope = {"type": "http", "method": "POST", "path": "/api", "client": ("10.0.0.1", 9000)}
    try:
        await app(scope, None, None)
    except RuntimeError:
        pass
    mock_send.assert_called_once()
    assert "POST" in mock_send.call_args[0][0]
    assert "/api" in mock_send.call_args[0][0]


@patch("watcherr.integrations.asgi.send_alert")
async def test_websocket_passthrough(mock_send):
    _setup()
    called = False

    async def ws_app(scope, receive, send):
        nonlocal called
        called = True

    app = WatcherrASGIMiddleware(ws_app)
    scope = {"type": "websocket", "path": "/ws"}
    await app(scope, None, None)
    assert called
    mock_send.assert_not_called()
