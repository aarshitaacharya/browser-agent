from playwright.async_api import Page
async def handle_click(action, page : Page):
    selector = action.get("selector")
    if not selector:
        return "Failed action: click - missing selector"
    try:
        await page.wait_for_selector(selector, timeout=10000)
        await page.click(selector)
        return "Executed action: click"
    except Exception as e:
        return f"Failed action: click - {str(e)}"
