from playwright.async_api import async_playwright

class BrowserSession:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def start(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
        if not self.browser:
            self.browser = await self.playwright.chromium.launch(headless=False)
        if not self.page:
            self.page = await self.browser.new_page()
    
    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


browser_session = BrowserSession()