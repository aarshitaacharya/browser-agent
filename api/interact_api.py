from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.gpt_parser import parse_command
from agents.browser_controller import execute_action
from browser_session import browser_session
from utils.logger import logger

router = APIRouter()

class InteractRequest(BaseModel):
    command: str

@router.post("/interact")
async def interact(request: InteractRequest):
    """
    Endpoint to receive natural language commands and execute them via browser automation.
    """
    try:
        logger.info(f"Received user command: {request.command}")
        parsed_actions = await parse_command(request.command)
        logger.info(f"Parsed plan: {parsed_actions}")
        result = await execute_action(parsed_actions, browser_session.page)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.exception("Interaction failed.")
        raise HTTPException(status_code=500, detail=str(e))
