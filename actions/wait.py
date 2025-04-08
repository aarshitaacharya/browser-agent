from playwright.async_api import Page
from utils.logger import logger


async def handle_wait(action: dict, page: Page) -> str:
    """
    Pauses the execution for a specified duration.

    Args:
        action (dict): Action dictionary containing 'duration' in milliseconds.
        page (Page): The Playwright page instance.

    Returns:
        str: Status message after performing the wait action.
    """
    duration = action.get("duration", 1000)

    try:
        await page.wait_for_timeout(duration)
        logger.info(f"Waited for {duration}ms.")
        return f"Executed action: wait {duration}ms"
    except Exception as e:
        logger.exception("Failed during wait.")
        return "Failed action: wait - internal error occurred"
