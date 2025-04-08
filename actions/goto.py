from playwright.async_api import Page
from urllib.parse import urlparse
from utils.logger import logger
from actions.captcha_solver import solve_amazon_captcha


async def handle_goto(action: dict, page: Page) -> str:
    """
    Navigates the browser to a specified URL. Triggers domain-specific handlers if needed.

    Args:
        action (dict): Action dictionary containing the 'url'.
        page (Page): The Playwright page instance.

    Returns:
        str: Status message indicating success or failure.
    """
    url = action.get("url")
    if not url:
        logger.warning("Goto action received without a URL.")
        return "Failed action: goto - missing URL"

    try:
        await page.goto(url)
        logger.info(f"Navigated to URL: {url}")

        # Currently only running on amazon's text captcha since google's image captcha needs 2Captcha which is paid
        domain = urlparse(url).netloc
        if "amazon." in domain:
            logger.info("Amazon domain detected — attempting CAPTCHA solve.")
            try:
                await solve_amazon_captcha(page)
            except Exception as captcha_error:
                logger.warning(f"CAPTCHA solve failed/skipped: {captcha_error}")

        return "Executed action: goto"

    except Exception as e:
        logger.exception("Goto action failed.")
        return f"Failed action: goto - {str(e)}"
