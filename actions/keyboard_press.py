from playwright.async_api import Page
from utils.logger import logger


async def handle_keyboard_press(action: dict, page: Page) -> str:
    """
    Simulates a keyboard key press on the current page.

    Args:
        action (dict): Action dictionary containing 'key'.
        page (Page): The Playwright page instance.

    Returns:
        str: Status message after attempting the key press.
    """
    key = action.get("key")
    if not key:
        logger.warning("Keyboard press action missing key.")
        return "Failed action: keyboard_press - missing key"

    try:
        await page.keyboard.press(key)
        logger.info(f"Pressed key: {key}")
        return "Executed action: keyboard_press"
    except Exception as e:
        logger.exception("Keyboard press failed.")
        return f"Failed action: keyboard_press - {str(e)}"
