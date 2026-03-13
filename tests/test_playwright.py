import sys
from unittest.mock import MagicMock, patch

import pytest

from watcherr import configure

# Mock playwright module for tests
if "playwright" not in sys.modules:
    sys.modules["playwright"] = MagicMock()

from watcherr.integrations.playwright import AsyncWatcherrPlaywright, WatcherrPlaywright


def _setup():
    configure(bot_token="123:TEST", chat_id="-999", service_name="test", rate_limit_seconds=0)


def _mock_page(url="https://example.com", screenshot=b"fake-png"):
    page = MagicMock()
    page.url = url
    page.screenshot.return_value = screenshot
    return page


@patch("watcherr.integrations.playwright.send_photo")
def test_sync_no_error_no_alert(mock_photo):
    _setup()
    page = _mock_page()
    with WatcherrPlaywright(page, name="test"):
        pass
    mock_photo.assert_not_called()


@patch("watcherr.integrations.playwright.send_photo")
def test_sync_error_sends_screenshot(mock_photo):
    _setup()
    page = _mock_page()
    try:
        with WatcherrPlaywright(page, name="login-test"):
            raise RuntimeError("click failed")
    except RuntimeError:
        pass
    mock_photo.assert_called_once()
    assert mock_photo.call_args[1]["filename"] == "login-test.png"
    assert mock_photo.call_args[1]["exc"] is not None


@patch("watcherr.integrations.playwright.send_alert")
@patch("watcherr.integrations.playwright.send_photo")
def test_sync_screenshot_failure_falls_back_to_alert(mock_photo, mock_alert):
    _setup()
    page = _mock_page()
    page.screenshot.side_effect = Exception("browser crashed")
    try:
        with WatcherrPlaywright(page, name="broken"):
            raise RuntimeError("test error")
    except RuntimeError:
        pass
    mock_photo.assert_not_called()
    mock_alert.assert_called_once()


@patch("watcherr.integrations.playwright.send_photo")
async def test_async_error_sends_screenshot(mock_photo):
    _setup()
    page = MagicMock()
    page.url = "https://example.com"

    async def fake_screenshot(**kwargs):
        return b"fake-png"

    page.screenshot = fake_screenshot
    try:
        async with AsyncWatcherrPlaywright(page, name="async-test"):
            raise ValueError("async error")
    except ValueError:
        pass
    mock_photo.assert_called_once()
    assert mock_photo.call_args[1]["filename"] == "async-test.png"


@patch("watcherr.integrations.playwright.send_photo")
async def test_async_no_error_no_alert(mock_photo):
    _setup()
    page = MagicMock()
    page.url = "https://example.com"

    async def fake_screenshot(**kwargs):
        return b"fake-png"

    page.screenshot = fake_screenshot
    async with AsyncWatcherrPlaywright(page, name="ok"):
        pass
    mock_photo.assert_not_called()
