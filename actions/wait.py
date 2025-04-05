from playwright.async_api import Page

async def handle_wait(action, page: Page):
    duration = action.get("duration", 1000)
    try:
        await page.wait_for_timeout(duration)
        return f"Executed action: wait {duration}ms"
    except Exception as e:
        return f"Failed action: wait - {str(e)}"