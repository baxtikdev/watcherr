from unittest.mock import patch

import pytest

flask = pytest.importorskip("flask")
from flask import Flask

from watcherr import configure
from watcherr.integrations.flask import init_app


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


def _create_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    init_app(app)

    @app.get("/ok")
    def ok():
        return {"status": "ok"}

    @app.get("/fail")
    def fail():
        raise RuntimeError("boom")

    return app


@patch("watcherr.integrations.flask.send_alert")
def test_successful_request_no_alert(mock_send):
    _setup()
    client = _create_app().test_client()
    resp = client.get("/ok")
    assert resp.status_code == 200
    mock_send.assert_not_called()


@patch("watcherr.integrations.flask.send_alert")
def test_exception_sends_alert(mock_send):
    _setup()
    client = _create_app().test_client()
    resp = client.get("/fail")
    assert resp.status_code == 500
    mock_send.assert_called_once()
    assert "GET" in mock_send.call_args[0][0]
    assert "/fail" in mock_send.call_args[0][0]


@patch("watcherr.integrations.flask.send_alert")
def test_404_no_alert(mock_send):
    _setup()
    client = _create_app().test_client()
    resp = client.get("/nonexistent")
    assert resp.status_code == 404
    mock_send.assert_not_called()
