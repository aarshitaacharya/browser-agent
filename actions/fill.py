from playwright.async_api import Page

async def handle_fill(action, page: Page):
    value = action.get("value")
    selector = action.get("selector")

    fallback_selectors = [
        selector,
        "textarea.gLFyf",                        # 🧠 Most reliable for Google homepage
        "input[name='q']",
        "input[title='Search']",
        "input[aria-label='Search']",
        "textarea[aria-label='Search']",
        "input.gLFyf",
    ]

    for sel in fallback_selectors:
        try:
            element = page.locator(sel)
            if await element.is_visible():
                await element.fill(value)
                return f"Executed action: fill using selector {sel}"
        except Exception as e:
            continue

    return f"Failed action: fill - could not find any working selector for {value}"
