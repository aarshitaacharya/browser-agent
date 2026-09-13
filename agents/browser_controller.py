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

        # If the browser window was closed or crashed mid-run, every
        # remaining action would fail with the same low-level error. One
        # clear message beats repeating that N times, and page.wait_for_timeout
        # itself would raise on a closed page.
        if page.is_closed():
            remaining = len(actions) - index - 1
            if remaining:
                logger.warning(f"Page closed mid-run; skipping {remaining} remaining action(s).")
                results.append(
                    f"Skipped {remaining} remaining action(s) - the browser window was closed."
                )
            break

        await page.wait_for_timeout(1000)

    return results
