from playwright.async_api import Page

async def handle_scroll(action, page: Page):
    direction = action.get("direction", "down")
    try:
        if direction == "down":
            await page.mouse.wheel(0, 500)
        elif direction == "up":
            await page.mouse.wheel(0, -500)
        else:
            return f"Failed action: scroll - invalid direction {direction}"
        return f"Executed action: scroll {direction}"
    except Exception as e:
        return f"Failed action: scroll - {str(e)}"