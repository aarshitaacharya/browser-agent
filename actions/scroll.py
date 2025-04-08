from playwright.async_api import Page
from utils.logger import logger


async def handle_scroll(action: dict, page: Page) -> str:
    """
    Scrolls the page up or down using the mouse wheel.

    Args:
        action (dict): Action dictionary with optional 'direction' ("up" or "down").
        page (Page): The Playwright page instance.

    Returns:
        str: Status message indicating the scroll result.
    """
    direction = action.get("direction", "down").lower()

    try:
        if direction == "down":
            await page.mouse.wheel(0, 500)
        elif direction == "up":
            await page.mouse.wheel(0, -500)
        else:
            logger.warning(f"Scroll action received invalid direction: {direction}")
            return f"Failed action: scroll - invalid direction '{direction}'"

        logger.info(f"Scrolled page: {direction}")
        return f"Executed action: scroll {direction}"

    except Exception as e:
        logger.exception("Scroll action failed.")
        return f"Failed action: scroll - {str(e)}"
