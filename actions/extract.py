from playwright.async_api import Page

async def handle_extract(action, page: Page):
    selector = action.get("selector")
    if not selector:
        return "Failed action: extract - missing selector"
    try:
        content = await page.inner_text(selector)
        return {"status": "success", "content": content}
    except Exception as e:
        return f"Failed action: extract - {str(e)}"
