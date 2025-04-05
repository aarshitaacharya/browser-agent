from playwright.async_api import Page

async def handle_keyboard_press(action, page: Page):
    key = action.get("key")
    if not key:
        return "Failed action: keyboard_press - missing key"
    try:
        await page.keyboard.press(key)
        return "Executed action: keyboard_press"
    except Exception as e:
        return f"Failed action: keyboard_press - {str(e)}"