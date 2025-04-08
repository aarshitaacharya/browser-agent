from playwright.async_api import Page, Frame
from utils.logger import logger


COMMON_POPUP_TEXTS = [
    "Accept", "I agree", "Reject", "Stay signed out",
    "No thanks", "Dismiss", "Got it", "Continue without signing in"
]


async def handle_dismiss_popup(action: dict, page: Page) -> str:
    """
    Attempts to dismiss common popups or consent banners on the page.

    Args:
        action (dict): The action dictionary (not used in this case).
        page (Page): The current Playwright page.

    Returns:
        str: Result message indicating whether a popup was dismissed or not.
    """
    logger.info("Attempting to dismiss common popups...")

    # we try to dismiss on the main page
    result = await _try_dismiss_in_context(page, context_name="main page")
    if result:
        return result

    # or dismissing within each iframe
    for frame in page.frames:
        result = await _try_dismiss_in_context(frame, context_name="iframe")
        if result:
            return result

    logger.warning("No known popup elements matched.")
    return "Failed action: dismiss_popup - no known elements matched (iframe-aware)"


async def _try_dismiss_in_context(context: Page | Frame, context_name: str) -> str | None:
    """
    Attempts to dismiss a popup within the given context (Page or Frame).

    Args:
        context (Page | Frame): A page or frame object to search in.
        context_name (str): For logging/debugging.

    Returns:
        Optional[str]: A success message if an element was clicked, else None.
    """
    for text in COMMON_POPUP_TEXTS:
        try:
            element = context.locator(f"text={text}")
            if await element.is_visible():
                await element.click()
                logger.info(f"Dismissed popup in {context_name}: '{text}'")
                return f"Executed action: dismiss_popup ({context_name} - {text})"
        except Exception as e:
            logger.debug(f"Popup text '{text}' not clickable in {context_name}: {e}")
            continue

    return None
