import re
import difflib
from playwright.async_api import Page
from api.extract_api import extract_elements_from_page
from utils.logger import logger

ORDINAL_MAP = {
    "first": 0,
    "second": 1,
    "third": 2,
    "fourth": 3,
    "fifth": 4,
    "last": -1,
}

# Maps the noun a user says to either an inferred role or a raw tag name.
ROLE_LOOKUP = {
    "login": "login_button",
    "product": "product_link",
    "add to cart": "add_to_cart_button",
    "submit": "submit_button",
    "search": "search_input",
    "video": "video",
    "link": "A",
    "image": "IMG",
    "button": "BUTTON",
}

ORDINAL_PATTERN = re.compile(
    r"(first|second|third|fourth|fifth|last)?\s*"
    r"(login|product|add to cart|submit|search|video|link|image|button)"
)


def is_similar(text1: str, text2: str, threshold: float = 0.6) -> bool:
    """
    Fuzzy similarity check between two strings.
    """
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio() > threshold


def matches_role(element: dict, role_target: str) -> bool:
    """
    Checks whether an extracted element matches a role name or a raw tag name.
    """
    return element.get("role") == role_target or element.get("tag") == role_target.upper()


async def click_element(element: dict, page: Page) -> str:
    """
    Clicks an extracted element by re-resolving it on the live page.

    The element carries the index it occupies among all nodes matching its own
    selector, so the right node is picked even when the selector is shared by
    many elements.

    Args:
        element (dict): An entry produced by extract_elements_from_page.
        page (Page): The Playwright page instance.

    Returns:
        str: Status message describing the outcome.
    """
    selector = element["selector_snippet"]
    index = element.get("index", 0)
    label = element.get("text") or element.get("alt") or selector

    try:
        handles = await page.query_selector_all(selector)
    except Exception as e:
        return f"Failed to click using selector '{selector}': {str(e)}"

    if index >= len(handles):
        return f"No visible element at position {index + 1} for selector '{selector}'"

    try:
        target = handles[index]
        await target.scroll_into_view_if_needed()
        await target.click()
        return f"Executed click on '{label}' (selector '{selector}' #{index + 1})"
    except Exception as e:
        return f"Failed to click on selector '{selector}' at position {index + 1}: {str(e)}"


async def handle_click(action: dict, page: Page) -> str:
    """
    Handles a click action on the page using, in order:
    1. Role and ordinal-based matching (e.g. "first button", "second product")
    2. Fuzzy text matching against the visible label of each element
    3. A direct selector provided by the LLM

    Args:
        action (dict): Dictionary containing 'query' or 'selector'.
        page (Page): The current Playwright page instance.

    Returns:
        str: Status message indicating the result of the click action.
    """
    query = action.get("query", "").lower().strip()
    selector = action.get("selector")

    if not query and not selector:
        return "Click failed - no query or selector provided"

    elements: list[dict] = []
    if query:
        logger.info(f"Handling click... Query: '{query}'")
        try:
            elements = await extract_elements_from_page(page)
        except Exception as e:
            logger.exception("DOM extraction failed during click.")
            return f"Failed to extract page elements: {str(e)}"

    # Priority 1: ordinal + role (e.g. "first button", "second product")
    role_match = ORDINAL_PATTERN.search(query) if query else None

    if role_match:
        ordinal = role_match.group(1) or "first"
        role = role_match.group(2)
        position = ORDINAL_MAP.get(ordinal, 0)
        role_target = ROLE_LOOKUP.get(role, role)

        filtered = [el for el in elements if matches_role(el, role_target)]

        if filtered:
            if position == -1:
                position = len(filtered) - 1
            if position < len(filtered):
                logger.info(
                    f"Matched {len(filtered)} '{role_target}' elements, "
                    f"targeting position {position + 1}."
                )
                return await click_element(filtered[position], page)
            return (
                f"Only {len(filtered)} element(s) matching role '{role_target}' "
                f"found, cannot click #{position + 1}"
            )

        logger.info(f"No element matched role '{role_target}', falling back to text match.")

    # Priority 2: fuzzy text match against element labels
    if query:
        best = best_text_match(elements, query)
        if best:
            logger.info(f"Fuzzy-matched query '{query}' to '{best.get('text')}'.")
            return await click_element(best, page)

    # Priority 3: use the selector the LLM handed us directly
    if selector:
        logger.info(f"Using selector from action: {selector}")
        try:
            await page.wait_for_selector(selector, timeout=10000)
            await page.click(selector)
            return f"Executed generic click using selector '{selector}'"
        except Exception as e:
            return f"Failed to click using selector '{selector}': {str(e)}"

    return "Click failed - no valid selector, tag, or role-based match found"


def best_text_match(elements: list[dict], query: str) -> dict | None:
    """
    Finds the element whose visible label most closely resembles the query.

    Args:
        elements (list[dict]): Extracted page elements.
        query (str): The user's natural language target.

    Returns:
        dict | None: The closest matching element, or None if nothing is close.
    """
    # Strip the ordinal words so "the second checkout button" compares on "checkout button".
    cleaned = re.sub(r"\b(first|second|third|fourth|fifth|last|the)\b", "", query).strip()
    if not cleaned:
        return None

    best, best_score = None, 0.0

    for el in elements:
        label = (el.get("text") or el.get("alt") or "").strip()
        if not label:
            continue

        score = difflib.SequenceMatcher(None, cleaned, label.lower()).ratio()
        # An exact substring hit is a stronger signal than raw edit distance.
        if cleaned in label.lower():
            score = max(score, 0.9)

        if score > best_score:
            best, best_score = el, score

    return best if best_score > 0.6 else None
