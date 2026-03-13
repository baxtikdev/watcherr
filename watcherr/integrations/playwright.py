from __future__ import annotations

import logging
from typing import TYPE_CHECKING

try:
    import playwright  # noqa: F401
except ImportError:
    raise ImportError("Install watcherr[playwright]: pip install watcherr[playwright]") from None

from watcherr.sender import send_alert, send_photo

if TYPE_CHECKING:
    from playwright.async_api import Page as AsyncPage
    from playwright.sync_api import Page as SyncPage

logger = logging.getLogger("watcherr")


class WatcherrPlaywright:
    """Sync context manager — captures screenshot and sends alert on exception.

    Usage:
        with WatcherrPlaywright(page, name="login-test"):
            page.goto("https://example.com")
            page.click("#submit")
    """

    def __init__(self, page: SyncPage, name: str = "playwright"):
        self._page = page
        self._name = name

    def __enter__(self) -> WatcherrPlaywright:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is None:
            return

        screenshot = self._take_screenshot()
        message = f"Playwright error in <b>{self._name}</b>"

        if screenshot:
            send_photo(
                photo=screenshot,
                caption=message,
                filename=f"{self._name}.png",
                exc=exc_val,
            )
        else:
            send_alert(message, exc=exc_val, url=self._get_url())

    def _take_screenshot(self) -> bytes | None:
        try:
            return self._page.screenshot(type="png", full_page=True, timeout=5000)
        except Exception:
            logger.debug("watcherr: screenshot failed", exc_info=True)
            return None

    def _get_url(self) -> str:
        try:
            return self._page.url
        except Exception:
            return "unknown"


class AsyncWatcherrPlaywright:
    """Async context manager — captures screenshot and sends alert on exception.

    Usage:
        async with AsyncWatcherrPlaywright(page, name="login-test"):
            await page.goto("https://example.com")
            await page.click("#submit")
    """

    def __init__(self, page: AsyncPage, name: str = "playwright"):
        self._page = page
        self._name = name

    async def __aenter__(self) -> AsyncWatcherrPlaywright:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_val is None:
            return

        screenshot = await self._take_screenshot()
        message = f"Playwright error in <b>{self._name}</b>"

        if screenshot:
            send_photo(
                photo=screenshot,
                caption=message,
                filename=f"{self._name}.png",
                exc=exc_val,
            )
        else:
            send_alert(message, exc=exc_val, url=self._get_url())

    async def _take_screenshot(self) -> bytes | None:
        try:
            return await self._page.screenshot(type="png", full_page=True, timeout=5000)
        except Exception:
            logger.debug("watcherr: screenshot failed", exc_info=True)
            return None

    def _get_url(self) -> str:
        try:
            return self._page.url
        except Exception:
            return "unknown"
