async def execute_action(actions: list, page):
    results = []

    for action in actions:
        try:
            if action["action"] == "goto":
                await page.goto(action["url"])

            elif action["action"] == "search":
                await page.fill('input[type="text"]', action["query"])
                await page.keyboard.press("Enter")

            elif action["action"] == "fill":
                selector = action.get("selector")
                value = action.get("value")
                if not selector or not value:
                    results.append("Failed action: fill - missing selector or value")
                else:
                    await page.fill(selector, value)

            elif action["action"] == "click":
                selector = action.get("selector")
                if not selector:
                    results.append("Failed action: click - missing selector")
                else:
                    await page.wait_for_selector(selector, timeout=10000)
                    await page.click(selector)

            elif action["action"] == "login":
                await page.goto(action["site"])
                await page.fill(action["email_selector"], action["email"])
                await page.fill(action["password_selector"], action["password"])
                await page.click(action["submit_selector"])

            else:
                results.append(f"Unknown action: {action['action']}")
                continue

            await page.wait_for_timeout(2000)
            results.append(f"Executed action: {action['action']}")

        except Exception as e:
            results.append(f"Failed action: {action['action']} - {str(e)}")

    return results