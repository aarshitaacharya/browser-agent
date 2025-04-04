from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from gpt_parser import parse_command
from browser_controller import execute_action

app = FastAPI()

class InteractRequest(BaseModel):
    command: str


@app.post("/interact")
async def interact(request: InteractRequest):
    try:
        parsed_action = await parse_command(request.command)
        result = await execute_action(parsed_action)
        return{"status": "success", "result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))