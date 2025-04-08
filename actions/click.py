import re
import httpx
import difflib
from typing import Optional
from playwright.async_api import Page
from utils.logger import logger


# Role-based matching (shared config could move this to constants.py later)
ORDINAL_MAP = {
    "first": 0,
    "second": 1,
    "third": 2,
    "fourth": 3
}

ROLE_LOOKUP = {
    "login": "login_button",
    "product": "product_link",
    "link": "link",
    "image": "IMG",
    "add to cart": "add_to_cart_button",
    "button": "BUTTON",
    "video": "VIDEO"
}


def is_similar(text1: str, text2: str) -> bool:
    """Check if two strings are roughly similar (fuzzy match)."""
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio() > 0.6


async def fetch_extracted_elements() -> Optional[list]:
    """Calls the extract API and returns extracted elements."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/extract")
            data = response.json()
            return data.get("elements", [])
    except Exception as e:
        logger.exception("Failed to call extract API.")
        return None

async def handle_click(action: dict, page: Page) -> str:
    """
    Handles clicking an element by role, ordinal, or direct selector.

    Args:
        action (dict): Should include 'query' or 'selector'.
        page (Page): The Playwright page.

    Returns:
        str: Click result message.
    """
    logger.info("Handling click action...")

    query = action.get("query", "").strip().lower()
    selector = action.get("selector")

    if not query and not selector:
        logger.warning("Click failed - no query or selector provided.")
        return "Click failed - no valid selector, tag, or role-based match found"

    elements = await fetch_extracted_elements()
    if not elements:
        return "Click failed - extract API returned no elements"

    logger.info(f"Click query: '{query}'")

    # riority 1: Match by role + ordinal (e.g. "first button", "second image") ---
    role_match = re.search(r"(first|second|third|fourth)?\s*(login|product|link|image|button|add to cart|video)", query)
    if role_match:
        ordinal = role_match.group(1) or "first"
        role = role_match.group(2)
        position = ORDINAL_MAP.get(ordinal, 0)
        role_target = ROLE_LOOKUP.get(role, role)

        filtered = [
            el for el in elements
            if el.get("role") == role_target or el.get("tag") == role_target.upper()
        ]

        if filtered:
            selector = filtered[0]["selector_snippet"]
            logger.info(f"Resolved selector from role '{role_target}': {selector}")
            try:
                element_handles = await page.query_selector_all(selector)
                if not element_handles or position >= len(element_handles):
                    return f"No visible element at position {position + 1} for selector '{selector}'"

                target = element_handles[position]
                await target.scroll_into_view_if_needed()
                await target.click()
                return f"Executed visible click on element with selector '{selector}' at position {position + 1}"
            except Exception as e:
                logger.exception("Failed clicking role-based element.")
                return f"Failed to click on selector '{selector}' at position {position + 1}: {str(e)}"

        else:
            logger.warning(f"No element found matching role '{role_target}'")
            return f"No element found matching role '{role_target}'"

    # Priority 2: LLM-specified selector
    if selector:
        logger.info(f"Attempting click using provided selector: {selector}")
        try:
            await page.wait_for_selector(selector, timeout=10000)
            await page.click(selector)
            return f"Executed generic click using selector '{selector}'"
        except Exception as e:
            logger.exception("Failed to click using provided selector.")
            return f"Failed to click using selector '{selector}': {str(e)}"

    return "Click failed - no valid selector, tag, or role-based match found"
