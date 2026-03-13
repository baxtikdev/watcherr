import tempfile
from pathlib import Path
from unittest.mock import patch

from watcherr import configure


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


@patch("watcherr.sender._dispatch_photo")
def test_send_photo_bytes(mock_dispatch):
    _setup()
    from watcherr import send_photo

    send_photo(b"fake-png-data", caption="test screenshot")
    mock_dispatch.assert_called_once()
    assert mock_dispatch.call_args[0][0] == b"fake-png-data"
    assert "test screenshot" in mock_dispatch.call_args[0][1]


@patch("watcherr.sender._dispatch_photo")
def test_send_photo_from_path(mock_dispatch):
    _setup()
    from watcherr import send_photo

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"fake-image")
        f.flush()
        send_photo(f.name, caption="from file")

    mock_dispatch.assert_called_once()
    assert mock_dispatch.call_args[0][0] == b"fake-image"


@patch("watcherr.sender._dispatch_photo")
def test_send_photo_with_exception(mock_dispatch):
    _setup()
    from watcherr import send_photo

    exc = ValueError("something broke")
    send_photo(b"img", caption="UI broken", exc=exc)
    mock_dispatch.assert_called_once()
    caption = mock_dispatch.call_args[0][1]
    assert "UI broken" in caption
    assert "ValueError" in caption


@patch("watcherr.sender._dispatch_photo")
def test_send_photo_nonexistent_file(mock_dispatch):
    _setup()
    from watcherr import send_photo

    send_photo("/nonexistent/file.png")
    mock_dispatch.assert_not_called()


@patch("watcherr.sender._dispatch_photo")
def test_send_photo_disabled(mock_dispatch):
    configure(bot_token="", chat_id="-999")
    from watcherr import send_photo

    send_photo(b"img")
    mock_dispatch.assert_not_called()
