from fastapi import APIRouter
from playwright.async_api import Error as PlaywrightError, Page
from bs4 import BeautifulSoup
from browser_session import browser_session
from utils.logger import logger

router = APIRouter()


@router.post("/extract")
async def extract_elements():
    """
    API endpoint to extract visible and interactive elements from the current browser page.

    Returns:
        dict: Contains list of elements and count, or error message.
    """
    page: Page | None = browser_session.page

    if not page:
        logger.warning("Extract failed: no active browser page.")
        return {"error": "No active browser page"}

    try:
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        tags_to_extract = ["a", "button", "img", "input"]
        extracted = []

        for tag in soup.find_all(tags_to_extract):
            tag_name = tag.name.upper()
            text = tag.get_text(strip=True)
            alt = tag.get("alt", "")
            src = tag.get("src") if tag.has_attr("src") else ""
            href = tag.get("href", "")

            selector = build_safe_selector(tag)
            if not selector:
                continue

            role = infer_role(tag, src)

            extracted.append({
                "tag": tag_name,
                "text": text,
                "alt": alt,
                "src": src,
                "href": href,
                "selector_snippet": selector,
                "role": role
            })

        logger.info(f"Extracted {len(extracted)} elements from page.")
        return {"elements": extracted, "count": len(extracted)}

    except PlaywrightError as e:
        logger.exception("Error during page content extraction.")
        return {"error": str(e)}


def build_safe_selector(tag) -> str | None:
    """
    Builds a simple CSS selector for the given tag.

    Args:
        tag (bs4.element.Tag): The HTML tag.

    Returns:
        str | None: A safe selector or None if not applicable.
    """
    tag_name = tag.name
    tag_id = tag.get("id")
    tag_class = tag.get("class")

    if tag_id:
        return f"{tag_name}#{tag_id}"
    elif tag_class:
        safe_class = tag_class[0].replace(" ", "").replace("\n", "")
        return f"{tag_name}.{safe_class}"
    else:
        return tag_name


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
    tag_id = tag.get("id", "").lower()
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
