import logging

# Shared logger for the whole backend. Writes to both a rotating-free file
# (agent.log, kept in .gitignore) and stdout, so a run can be replayed from
# the log after the fact while still showing live in the uvicorn console.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("browser-agent")
