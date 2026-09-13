import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from browser_session import browser_session
from agents.gpt_parser import parse_command
from fastapi.middleware.cors import CORSMiddleware
from api.extract_api import router as extract_router
from api.interact_api import router as interact_router

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")


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

app = FastAPI(title="Browser AI Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(extract_router)
app.include_router(interact_router)


@app.get("/health")
async def health():
    """
    Lightweight readiness probe. The frontend polls this so the mic can tell
    the user whether the agent is actually listening on the other end.

    Checks that the page is genuinely open, not just that a reference to one
    exists - a closed browser window still leaves browser_session.page set to
    a now-unusable Page object.
    """
    return {
        "status": "ok",
        "browser_ready": browser_session.is_alive(),
    }
