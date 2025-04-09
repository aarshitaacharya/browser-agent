from actions import ACTION_HANDLERS
from utils.logger import logger
from playwright.async_api import Page


async def execute_action(actions: list[dict], page: Page) -> list[str]:
    """
    Executes a list of structured browser actions using their corresponding handlers.

    Args:
        actions (list[dict]): List of action dictionaries from the planner or LLM.
        page (Page): The Playwright page object.

    Returns:
        list[str]: Status results from each action.
    """
    results = []

    for index, action in enumerate(actions):
        action_type = action.get("action")
        handler = ACTION_HANDLERS.get(action_type)

        if not handler:
            message = f"Unknown action: {action_type}"
            logger.warning(message)
            results.append(message)
            continue

        logger.info(f"Executing action {index + 1}/{len(actions)}: {action_type}")

        try:
            result = await handler(action, page)
        except Exception as e:
            logger.exception(f"Handler for '{action_type}' failed.")
            result = f"Failed action: {action_type} - {str(e)}"

        results.append(result)
        await page.wait_for_timeout(1000)

    return results
