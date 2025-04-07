import re
import httpx
from playwright.async_api import Page
import difflib

def is_similar(text1, text2):
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio() > 0.6


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

    role_match = re.search(r"(first|second|third|fourth)?\s*(login|product|link|image|button|add to cart)", query)

    if role_match:
        ordinal = role_match.group(1) or "first"
        role = role_match.group(2)

        role_lookup = {
            "login": "login_button",
            "product": "product_link",
            "link": "link",  
            "image": "IMG",
            "add to cart": "add_to_cart_button",
            "button": "BUTTON",
            
        }

        position = ordinal_map.get(ordinal, 0)
        role_target = role_lookup.get(role, role)

        filtered = [
            el for el in elements
            if el.get("role") == role_target or el.get("tag") == role_target.upper()
        ]

        if filtered:
            selector = filtered[0]["selector_snippet"]  # Use first match to extract selector
            try:
                # Get all elements matching that selector from the **live page**
                element_handles = await page.query_selector_all(selector)

                if not element_handles or position >= len(element_handles):
                    return f"No visible element at position {position + 1} for selector '{selector}'"

                target = element_handles[position]
                await target.scroll_into_view_if_needed()
                await target.click()
                return f"Executed visible click on element with selector '{selector}' at position {position + 1}"
            except Exception as e:
                return f"Failed to click on selector '{selector}' at position {position + 1}: {str(e)}"
        else:
            return f"No element found matching role '{role_target}'"

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