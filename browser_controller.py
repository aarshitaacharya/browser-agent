from playwright.async_api import async_playwright

async def execute_action(action: dict):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        if action['action'] == 'goto':
            await page.goto(action['url'])
        
        elif action['action'] == 'search':
            await page.goto(action['site'])
            await page.fill('input[type="text"]', action['query'])
            await page.keyboard.press('Enter')
        
        elif action['action'] == 'click':
            await page.click(action['selector'])
        
        elif action['action'] == 'fill':
            await page.fill(action['selector'], action['value'])
        
        elif action['action'] == 'login':
            await page.goto(action['site'])
            await page.fill(action['email_selector'], action['email'])
            await page.fill(action['password_selector'], action['password'])
            await page.click(action['submit_selector'])
        
        else:
            return f"Unknown action: {action['action']}"
        
        await page.wait_for_timeout(5000)  # Wait for 5 seconds to see the result
        await browser.close()
        return f"Executed action: {action['action']}"