from fastapi import FastAPI, HTTPException, Request, Depends
from contextlib import asynccontextmanager
from pydantic import BaseModel
from gpt_parser import parse_command
from browser_controller import execute_action
from browser_session import browser_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    await browser_session.start()
    yield
    await browser_session.stop()


app = FastAPI(lifespan=lifespan)

class InteractRequest(BaseModel):
    command: str

@app.post("/interact")
async def interact(request: InteractRequest):
    try:
        parsed_action = await parse_command(request.command)
        result = await execute_action(parsed_action, browser_session.page)
        return{"status": "success", "result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))