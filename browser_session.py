import asyncio
import os
from playwright.async_api import async_playwright, Playwright, Browser, Page
from utils.logger import logger

# Watching the agent work is most of the point, so the browser is visible by
# default. Set HEADLESS=1 to run it without a window (CI, remote boxes).
HEADLESS = os.getenv("HEADLESS", "").lower() in {"1", "true", "yes"}


class BrowserSession:
    """
    Singleton-style wrapper for managing a persistent Playwright browser session.

    The browser is user-visible by default, which means a user can close the
    window (or the OS can kill the process) without the app knowing. Every
    caller should go through ensure_ready() rather than reading .page
    directly, so a dead browser is relaunched transparently instead of every
    subsequent action failing with a raw Playwright "Target closed" error.
    """

    def __init__(self):
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None
        # Guards start()/stop() against concurrent requests racing to restart
        # a dead session at the same time.
        self._lock = asyncio.Lock()

    def is_alive(self) -> bool:
        """
        Reports whether there is a usable page right now, without touching
        the browser. False after the window is closed or the browser process
        dies, even though self.page still holds a (now-unusable) reference.
        """
        return bool(
            self.browser
            and self.browser.is_connected()
            and self.page
            and not self.page.is_closed()
        )

    async def start(self) -> None:
        """
        Starts the Playwright engine and browser if not already running.
        Creates a new browser page.
        """
        async with self._lock:
            await self._start_locked()

    async def _start_locked(self) -> None:
        if not self.playwright:
            self.playwright = await async_playwright().start()
            logger.info("Playwright engine started.")

        if not self.browser or not self.browser.is_connected():
            self.browser = await self.playwright.chromium.launch(headless=HEADLESS)
            logger.info(f"Chromium browser launched (headless={HEADLESS}).")

        if not self.page or self.page.is_closed():
            self.page = await self.browser.new_page()
            logger.info("New browser page created.")

    async def ensure_ready(self) -> Page:
        """
        Returns a live page, relaunching the browser first if it crashed or
        was closed since the last call.

        Every API route should call this instead of reading .page directly.

        Returns:
            Page: A page guaranteed to be open at the moment this returns.

        Raises:
            RuntimeError: If a fresh browser could not be launched.
        """
        if self.is_alive():
            return self.page

        async with self._lock:
            # Re-check inside the lock: another request may have already
            # restarted the session while this one was waiting.
            if not self.is_alive():
                logger.warning("Browser session is not alive; restarting it.")
                await self._stop_locked()
                await self._start_locked()

        if not self.page:
            raise RuntimeError("Failed to start a browser session.")

        return self.page

    async def stop(self) -> None:
        """
        Stops the browser and Playwright instance if active.
        """
        async with self._lock:
            await self._stop_locked()

    async def _stop_locked(self) -> None:
        self.page = None

        if self.browser:
            try:
                await self.browser.close()
                logger.info("Browser closed.")
            except Exception as e:
                # The browser may already be gone (window closed, process
                # killed) - closing a dead handle is a no-op, not a failure.
                logger.debug(f"Browser close skipped/failed (likely already dead): {e}")
            self.browser = None

        if self.playwright:
            try:
                await self.playwright.stop()
                logger.info("Playwright engine stopped.")
            except Exception as e:
                logger.debug(f"Playwright stop skipped/failed: {e}")
            self.playwright = None

browser_session = BrowserSession()
