from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from agents.gpt_parser import parse_command
from agents.browser_controller import execute_action
from browser_session import browser_session
from utils.logger import logger

router = APIRouter()

# Prefixes the action handlers use to mark a step that did not work. Kept in
# sync with isFailure() in the frontend so the log colours and the spoken
# summary never disagree about what failed.
FAILURE_PREFIXES = ("failed", "click failed", "unknown action", "no ", "skipped")


class InteractRequest(BaseModel):
    command: str = Field(..., min_length=1, description="Natural language instruction.")
    source: Literal["text", "voice"] = "text"


def summarize(results: list[str]) -> str:
    """
    Condenses a run's per-step results into one sentence suitable for reading
    aloud with speech synthesis.

    Args:
        results (list[str]): Per-action status messages.

    Returns:
        str: A short spoken summary.
    """
    if not results:
        return "I could not work out any steps for that."

    failed = [r for r in results if r.lower().startswith(FAILURE_PREFIXES)]
    done = len(results) - len(failed)

    def steps(n: int) -> str:
        return f"{n} step" if n == 1 else f"{n} steps"

    if not failed:
        return f"Done. I completed {steps(done)}."
    if done == 0:
        return f"That did not work. All {steps(len(failed))} failed."
    return f"I completed {steps(done)}, but {len(failed)} failed."


@router.post("/interact")
async def interact(request: InteractRequest):
    """
    Endpoint to receive natural language commands and execute them via browser automation.

    Accepts commands typed into the UI or dictated through the browser's Web
    Speech API; `source` only affects logging and the spoken summary.
    """
    command = request.command.strip()
    if not command:
        raise HTTPException(status_code=400, detail="Command must not be empty.")

    try:
        # Transparently relaunches the browser if the window was closed or
        # crashed since the last request, instead of failing on a stale page.
        page = await browser_session.ensure_ready()
    except Exception as e:
        logger.exception("Could not start a browser session.")
        raise HTTPException(status_code=503, detail=f"Browser session is not available: {e}")

    try:
        logger.info(f"Received {request.source} command: {command}")
        parsed_actions = await parse_command(command)
        logger.info(f"Parsed plan: {parsed_actions}")
        result = await execute_action(parsed_actions, page)
        return {
            "status": "success",
            "result": result,
            "plan": parsed_actions,
            "spoken_summary": summarize(result),
        }
    except ValueError as e:
        # The model returned something we could not turn into a plan.
        logger.warning(f"Could not parse a plan for command: {command}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Interaction failed.")
        raise HTTPException(status_code=500, detail=str(e))
