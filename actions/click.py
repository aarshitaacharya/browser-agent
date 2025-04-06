import re
import httpx
from playwright.async_api import Page

async def handle_click(action: dict, page: Page):
    print("Using extract API to find elements for click...")

    # Call extract API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/extract")
            data = response.json()
    except Exception as e:
        return f"Failed to call extract API: {str(e)}"

    if "elements" not in data:
        return "No elements returned from extract API"

    elements = data["elements"]
    query = action.get("query", "").lower().strip()

    print("Handling click...")
    print(f"Click Query: {query}")

    if not query:
        return "Click failed - no query provided"

    # Priority 1: Match by ordinal + role
    ordinal_map = {
        "first": 0,
        "second": 1,
        "third": 2,
        "fourth": 3
    }

    role_match = re.search(r"(first|second|third|fourth)?\s*(login|product|link|image|button)", query)
    if role_match:
        ordinal = role_match.group(1) or "first"
        role = role_match.group(2)

        role_lookup = {
            "login": "login_button",
            "product": "product_link",
            "link": "link",  # fallback to tag if no role match
            "image": "IMG",
            "button": "BUTTON"
        }

        position = ordinal_map.get(ordinal, 0)
        role_target = role_lookup.get(role, role)

        filtered = [
            el for el in elements
            if el.get("role") == role_target or el.get("tag") == role_target.upper()
        ]

        if filtered and position < len(filtered):
            selector = filtered[position]["selector_snippet"]
            try:
                await page.wait_for_selector(selector, timeout=10000)
                await page.click(selector)
                return f"Executed dynamic click on element with selector '{selector}' (text: '{filtered[position]['text']}')"
            except Exception as e:
                return f"Failed to click on selector '{selector}': {str(e)}"
        else:
            return f"No element found matching role '{role_target}' at position {position + 1}"

    # Priority 2: Use LLM-specified selector if present
    selector = action.get("selector")
    if selector:
        try:
            await page.wait_for_selector(selector, timeout=10000)
            await page.click(selector)
            return f"Executed generic click using selector '{selector}'"
        except Exception as e:
            return f"Failed to click using selector '{selector}': {str(e)}"

    return "Click failed - no valid selector, tag, or role-based match found"
