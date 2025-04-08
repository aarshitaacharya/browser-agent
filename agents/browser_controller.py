from actions import ACTION_HANDLERS

async def execute_action(actions: list, page):
    results = []

    for action in actions:
        action_type = action.get("action")
        handler = ACTION_HANDLERS.get(action_type)

        if not handler:
            results.append(f"Unknown action: {action_type}")
            continue

        try:
            result = await handler(action, page)
        except Exception as e:
            result = f"Failed action: {action_type} - {str(e)}"

        results.append(result)
        await page.wait_for_timeout(1000)

    return results
