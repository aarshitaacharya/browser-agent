from playwright.async_api import Page
from utils.logger import logger


async def handle_screenshot(action: dict, page: Page) -> str:
    """
    Captures a screenshot of the current page.

    Args:
        action (dict): Action dictionary that may contain a 'path'.
        page (Page): The Playwright page instance.

    Returns:
        str: Status message indicating the result of the screenshot action.
    """
    path = action.get("path", "screenshot.png")

    try:
        await page.screenshot(path=path, full_page=True)
        logger.info(f"Screenshot saved to: {path}")
        return f"Executed action: screenshot saved to {path}"
    except Exception as e:
        logger.exception("Screenshot action failed.")
        return f"Failed action: screenshot - {str(e)}"
