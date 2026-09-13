from fastapi import APIRouter
from playwright.async_api import Error as PlaywrightError, Page
from bs4 import BeautifulSoup
from browser_session import browser_session
from utils.logger import logger

router = APIRouter()

TAGS_TO_EXTRACT = ["a", "button", "img", "input"]


async def extract_elements_from_page(page: Page) -> list[dict]:
    """
    Parses the current DOM into a flat list of interactive elements.

    Each element carries a CSS selector plus the index it occupies among all
    elements matching that same selector, so a caller can address the Nth
    element of a role without re-deriving it from the live page.

    Args:
        page (Page): The Playwright page instance.

    Returns:
        list[dict]: Structured descriptions of interactive elements.
    """
    content = await page.content()
    soup = BeautifulSoup(content, "html.parser")

    extracted = []
    seen_selectors: dict[str, int] = {}

    for tag in soup.find_all(TAGS_TO_EXTRACT):
        selector = build_safe_selector(tag)
        if not selector:
            continue

        src = tag.get("src") if tag.has_attr("src") else ""

        # How many earlier elements already used this selector. Playwright's
        # query_selector_all returns nodes in document order, so this doubles
        # as the position of this element within that selector's matches.
        index = seen_selectors.get(selector, 0)
        seen_selectors[selector] = index + 1

        extracted.append({
            "tag": tag.name.upper(),
            "text": tag.get_text(strip=True),
            "alt": tag.get("alt", ""),
            "src": src,
            "href": tag.get("href", ""),
            "selector_snippet": selector,
            "index": index,
            "role": infer_role(tag, src),
        })

    return extracted


@router.post("/extract")
async def extract_elements():
    """
    API endpoint to extract visible and interactive elements from the current browser page.

    Returns:
        dict: Contains list of elements and count, or error message.
    """
    try:
        page = await browser_session.ensure_ready()
    except Exception as e:
        logger.warning(f"Extract failed: no active browser page ({e}).")
        return {"error": "No active browser page"}

    try:
        extracted = await extract_elements_from_page(page)
        logger.info(f"Extracted {len(extracted)} elements from page.")
        return {"elements": extracted, "count": len(extracted)}

    except PlaywrightError as e:
        logger.exception("Error during page content extraction.")
        return {"error": str(e)}


def build_safe_selector(tag) -> str | None:
    """
    Builds a simple CSS selector for the given tag.

    Attribute selectors are used instead of `#id` / `.class` shorthand so that
    ids and class names containing CSS-special characters (":", "/", leading
    digits) don't produce a selector Playwright refuses to parse.

    Args:
        tag (bs4.element.Tag): The HTML tag.

    Returns:
        str | None: A safe selector or None if not applicable.
    """
    tag_name = tag.name
    tag_id = tag.get("id")
    tag_class = tag.get("class")

    if tag_id:
        return f'{tag_name}[id="{escape_attr(tag_id)}"]'
    elif tag_class:
        first_class = tag_class[0].strip()
        if first_class:
            return f'{tag_name}[class~="{escape_attr(first_class)}"]'

    return tag_name


def escape_attr(value: str) -> str:
    """
    Escapes a value for safe use inside a double-quoted CSS attribute selector.
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def infer_role(tag, src: str = "") -> str:
    """
    Infers the semantic role of an element based on its attributes.

    Args:
        tag (bs4.element.Tag): The HTML tag.
        src (str): Optional src for images.

    Returns:
        str: Inferred role name.
    """
    tag_name = tag.name.lower()
    text = (
        tag.get_text(strip=True).lower()
        + tag.get("value", "").lower()
        + tag.get("name", "").lower()
        + tag.get("id", "").lower()
    )

    alt = tag.get("alt", "").lower()
    href = tag.get("href", "") or ""
    name = tag.get("name", "").lower()
    placeholder = tag.get("placeholder", "").lower()
    classes = " ".join(tag.get("class", [])).lower()

    if tag_name in ["a", "button", "input"] and "login" in text:
        return "login_button"
    if tag_name == "button" and "add to cart" in text:
        return "add_to_cart_button"
    if tag_name == "input" and tag.get("type") == "submit" and "login" in text:
        return "login_button"
    if tag_name == "input" and ("search" in name or "search" in placeholder):
        return "search_input"
    if tag_name == "img" and ("logo" in alt or "logo" in tag.get("src", "")):
        return "logo"
    if tag_name in ["a", "img"] and any(x in href for x in ["/product", "?pid=", "/p/"]):
        return "product_link"
    if tag_name == "button" and "submit" in text:
        return "submit_button"
    if tag_name == "input" and tag.get("type") == "submit":
        return "submit_button"
    if tag_name in ["a", "img"] and (
        any(sub in href for sub in ["item_", "product", "pid", "/p/", "/product"]) or
        "inventory_item" in classes
    ):
        return "product_link"
    if tag.name == "a" and tag.get("id") == "thumbnail":
        return "video"

    return "unknown"
