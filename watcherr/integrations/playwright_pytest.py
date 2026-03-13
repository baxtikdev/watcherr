"""Pytest plugin for Playwright test failure alerts with screenshots.

Register in conftest.py:
    pytest_plugins = ["watcherr.integrations.playwright_pytest"]

Or via pyproject.toml:
    [tool.pytest.ini_options]
    plugins = ["watcherr.integrations.playwright_pytest"]

Requires a `page` fixture (provided by pytest-playwright).
"""

from __future__ import annotations

import logging

import pytest

from watcherr.sender import send_alert, send_photo

logger = logging.getLogger("watcherr")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    page = _get_page_from_item(item)
    test_name = item.nodeid
    exc_info = call.excinfo

    exc = exc_info.value if exc_info else None
    message = f"Test failed: <b>{test_name}</b>"

    if page is not None:
        screenshot = _take_screenshot(page, test_name)
        if screenshot:
            send_photo(
                photo=screenshot,
                caption=message,
                filename=f"{item.name}.png",
                exc=exc,
            )
            return

    send_alert(message, exc=exc, test=test_name)


def _get_page_from_item(item) -> object | None:
    """Extract Playwright page from test fixtures."""
    for name in ("page", "playwright_page"):
        if name in item.funcargs:
            return item.funcargs[name]
    return None


def _take_screenshot(page, test_name: str) -> bytes | None:
    try:
        return page.screenshot(type="png", full_page=True, timeout=5000)
    except Exception:
        logger.debug("watcherr: screenshot failed for %s", test_name, exc_info=True)
        return None
