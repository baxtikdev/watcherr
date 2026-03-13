import sys
from unittest.mock import MagicMock, patch

from watcherr import configure

# Mock sanic if not installed
if "sanic" not in sys.modules:
    sanic_mock = MagicMock()
    sanic_mock.exceptions.SanicException = type("SanicException", (Exception,), {})
    sys.modules["sanic"] = sanic_mock
    sys.modules["sanic.exceptions"] = sanic_mock.exceptions

from watcherr.integrations.sanic_middleware import init_app


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


@patch("watcherr.integrations.sanic_middleware.send_alert")
def test_init_app_registers_handler(mock_send):
    _setup()
    app = MagicMock()
    init_app(app)
    app.exception.assert_called_once_with(Exception)


@patch("watcherr.integrations.sanic_middleware.send_alert")
async def test_handler_sends_alert_on_exception(mock_send):
    _setup()
    app = MagicMock()

    captured = {}
    app.exception.return_value = lambda fn: captured.update(handler=fn) or fn

    init_app(app)

    request = MagicMock()
    request.method = "GET"
    request.path = "/fail"
    request.remote_addr = "10.0.0.1"
    request.ip = "10.0.0.1"
    exc = RuntimeError("boom")

    try:
        await captured["handler"](request, exc)
    except RuntimeError:
        pass

    mock_send.assert_called_once()
    assert "GET" in mock_send.call_args[0][0]
    assert "/fail" in mock_send.call_args[0][0]
