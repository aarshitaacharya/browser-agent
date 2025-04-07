from playwright.async_api import Page
from urllib.parse import urlparse
from actions.captcha_solver import solve_amazon_captcha

# actions/goto.py
async def handle_goto(action, page: Page):
    url = action.get("url")
    if not url:
        return "Failed action: goto - missing URL"
    try:
        await page.goto(url)
        try:
            domain = urlparse(action["url"]).netloc
            if "amazon." in domain:
                await solve_amazon_captcha(page)
        except Exception as captcha_e:
            print("🛡️ CAPTCHA check failed or skipped:", captcha_e)

        return "Executed action: goto"
    except Exception as e:
        return f"Failed action: goto - {str(e)}"