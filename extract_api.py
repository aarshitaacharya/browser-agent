from fastapi import APIRouter
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page
from browser_session import browser_session
from bs4 import BeautifulSoup

router = APIRouter()

@router.post("/extract")
async def extract_elements():
    page = browser_session.page

    if not page:
        return {"error": "No active browser page"}

    try:
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        # Extract only visible and interactive elements
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

        return {"elements": extracted, "count": len(extracted)}

    except PlaywrightError as e:
        return {"error": str(e)}


def build_safe_selector(tag):
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

def infer_role(tag, src=""):
    tag_name = tag.name.lower()
    text = tag.get_text(strip=True).lower()
    alt = tag.get("alt", "").lower()
    href = tag.get("href", "") or ""
    name = tag.get("name", "").lower()
    placeholder = tag.get("placeholder", "").lower()
    tag_id = tag.get("id", "").lower()
    classes = " ".join(tag.get("class", [])).lower()

    if tag_name in ["a", "button"] and any(keyword in text for keyword in ["login", "sign in"]):
        return "login_button"
    if tag_name == "input" and ("search" in name or "search" in placeholder):
        return "search_input"
    if tag_name == "img" and ("logo" in alt or "logo" in src):
        return "logo"
    if tag_name in ["a", "img"] and any(x in href for x in ["/product", "?pid=", "/p/"]):
        return "product_link"
    if tag_name == "button" and "submit" in text:
        return "submit_button"
    if tag_name == "input" and tag.get("type") == "submit":
        return "submit_button"
    return "unknown"
