from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from watcherr import configure
from watcherr.integrations.fastapi_middleware import WatcherrMiddleware


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


def _create_app():
    app = FastAPI()
    app.add_middleware(WatcherrMiddleware)

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    @app.get("/fail")
    async def fail():
        raise RuntimeError("boom")

    return app


@patch("watcherr.integrations.fastapi_middleware.send_alert")
def test_successful_request_no_alert(mock_send):
    _setup()
    client = TestClient(_create_app(), raise_server_exceptions=False)
    resp = client.get("/ok")
    assert resp.status_code == 200
    mock_send.assert_not_called()


@patch("watcherr.integrations.fastapi_middleware.send_alert")
def test_exception_sends_alert(mock_send):
    _setup()
    client = TestClient(_create_app(), raise_server_exceptions=False)
    resp = client.get("/fail")
    assert resp.status_code == 500
    mock_send.assert_called_once()
    call_args = mock_send.call_args
    assert "GET" in call_args[0][0]
    assert "/fail" in call_args[0][0]
    assert isinstance(call_args[1]["exc"], RuntimeError)
