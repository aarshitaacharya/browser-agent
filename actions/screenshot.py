from playwright.async_api import Page

async def handle_screenshot(action, page: Page):
    path = action.get("path", "screenshot.png")
    try:
        await page.screenshot(path=path, full_page=True)
        return f"Executed action: screenshot saved to {path}"
    except Exception as e:
        return f"Failed action: screenshot - {str(e)}"
