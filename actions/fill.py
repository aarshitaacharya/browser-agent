from playwright.async_api import Page
from utils.logger import logger

DEFAULT_FALLBACK_SELECTORS = [
    "textarea.gLFyf",                      
    "input[name='q']",
    "input[title='Search']",
    "input[aria-label='Search']",
    "textarea[aria-label='Search']",
    "input.gLFyf"
]


async def handle_fill(action: dict, page: Page) -> str:
    """
    Fills a text input field with the specified value using a selector or fallback options.

    Args:
        action (dict): Action dictionary containing 'value' and optionally 'selector'.
        page (Page): The Playwright page instance.

    Returns:
        str: Status message after attempting the fill.
    """
    value = action.get("value")
    selector = action.get("selector")

    if not value:
        logger.warning("Fill action missing value.")
        return "Failed action: fill - no value provided"

    fallback_selectors = [selector] if selector else []
    fallback_selectors.extend(DEFAULT_FALLBACK_SELECTORS)

    for sel in fallback_selectors:
        if not sel:
            continue
        try:
            element = page.locator(sel)
            if await element.is_visible():
                await element.fill(value)
                logger.info(f"Filled '{value}' into selector: {sel}")
                return f"Executed action: fill using selector {sel}"
        except Exception as e:
            logger.debug(f"Selector '{sel}' failed during fill: {e}")
            continue

    logger.error(f"Fill failed for value '{value}'. No working selector found.")
    return f"Failed action: fill - could not find any working selector for '{value}'"
