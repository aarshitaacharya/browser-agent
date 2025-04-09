from fastapi import FastAPI
from contextlib import asynccontextmanager
from browser_session import browser_session
from agents.gpt_parser import parse_command
from fastapi.middleware.cors import CORSMiddleware
from api.extract_api import router as extract_router
from api.interact_api import router as interact_router  # NEW

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting browser session...")
    await browser_session.start()

    app.state.page = browser_session.page

    print("Warming up LLM...")
    try:
        await parse_command("Ping")
        print("LLM is ready.")
    except Exception as e:
        print(f"LLM warm-up failed: {e}")

    yield

    print("Stopping browser session...")
    await browser_session.stop()

app = FastAPI(lifespan=lifespan)

app.include_router(extract_router)
app.include_router(interact_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)