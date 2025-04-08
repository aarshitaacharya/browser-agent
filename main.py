from fastapi import FastAPI, HTTPException, Request, Depends
from contextlib import asynccontextmanager
from pydantic import BaseModel
from agents.gpt_parser import parse_command
from agents.browser_controller import execute_action
from browser_session import browser_session
from fastapi.middleware.cors import CORSMiddleware
from api.extract_api import router as extract_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting browser session...")
    await browser_session.start()

    app.state.page = browser_session.page

    print("🧠 Pinging LLM to warm it up...")
    try:
        await parse_command("Ping")  # This gets the model into memory
        print("✅ LLM warmed up and ready.")
    except Exception as e:
        print(f"⚠️ Failed to warm up LLM: {e}")

    yield

    print("🧹 Shutting down browser session...")
    await browser_session.stop()

app = FastAPI(lifespan=lifespan)
app.include_router(extract_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InteractRequest(BaseModel):
    command: str

@app.post("/interact")
async def interact(request: InteractRequest):
    try:
        print("📩 Sending command to LLM...")
        parsed_action = await parse_command(request.command)
        print("✅ Received parsed command:", parsed_action)
        result = await execute_action(parsed_action, browser_session.page)
        return{"status": "success", "result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))