from playwright.async_api import Page

# actions/goto.py
async def handle_goto(action, page: Page):
    url = action.get("url")
    if not url:
        return "Failed action: goto - missing URL"
    try:
        await page.goto(url)
        return "Executed action: goto"
    except Exception as e:
        return f"Failed action: goto - {str(e)}"