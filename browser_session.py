from playwright.async_api import async_playwright, Playwright, Browser, Page
from utils.logger import logger


class BrowserSession:
    """
    Singleton-style wrapper for managing a persistent Playwright browser session.
    """

    def __init__(self):
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    async def start(self) -> None:
        """
        Starts the Playwright engine and browser if not already running.
        Creates a new browser page.
        """
        if not self.playwright:
            self.playwright = await async_playwright().start()
            logger.info("Playwright engine started.")

        if not self.browser:
            self.browser = await self.playwright.chromium.launch(headless=False)
            logger.info("Chromium browser launched.")

        if not self.page:
            self.page = await self.browser.new_page()
            logger.info("New browser page created.")

    async def stop(self) -> None:
        """
        Stops the browser and Playwright instance if active.
        """
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed.")
            self.browser = None

        if self.playwright:
            await self.playwright.stop()
            logger.info("Playwright engine stopped.")
            self.playwright = None
            self.page = None

browser_session = BrowserSession()
