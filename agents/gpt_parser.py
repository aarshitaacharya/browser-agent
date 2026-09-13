import json
import os
import re
from pathlib import Path
from ollama import AsyncClient
from utils.logger import logger

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# AsyncClient keeps the FastAPI event loop free while the model is generating.
client = AsyncClient(host=OLLAMA_HOST)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EXAMPLES_PATH = PROJECT_ROOT / "prompts" / "prompt_examples.txt"

# Matches the outermost JSON array or object in a blob of model output.
JSON_BLOCK_PATTERN = re.compile(r"(\[.*\]|\{.*\})", re.DOTALL)


def load_prompt_examples(file_path: str | Path = DEFAULT_EXAMPLES_PATH) -> str:
    """
    Loads prompt examples from a text file to prime the LLM.

    Args:
        file_path (str | Path): Path to the prompt examples file.

    Returns:
        str: Prompt examples as a single string.
    """
    try:
        return Path(file_path).read_text()
    except FileNotFoundError:
        logger.error(f"Prompt examples file not found at path: {file_path}")
        return ""


# Static system prompt (few-shot instructions + examples)
SYSTEM_PROMPT = (
    "You are a browser automation agent.\n"
    "Translate user commands into a JSON array of actions.\n"
    "Use only the following action types:\n"
    "- goto\n- fill\n- click\n- keyboard_press\n- wait\n"
    "- scroll\n- screenshot\n- dismiss_popup\n\n"
    "Each action should be a dictionary. Return only the raw JSON array, "
    "with no explanation and no markdown code fences.\n\n"
    "The command may have been dictated by voice, so it can contain "
    "transcription quirks: spelled-out punctuation (\"dot com\"), missing "
    "capitalisation, or filler words. Interpret it charitably.\n\n"
    + load_prompt_examples()
)


def extract_json(content: str) -> list[dict]:
    """
    Pulls a JSON action list out of raw model output.

    Small local models routinely wrap their answer in ```json fences or add a
    sentence of commentary, so a plain json.loads on the whole response is not
    reliable enough on its own.

    Args:
        content (str): Raw text returned by the model.

    Returns:
        list[dict]: Parsed list of actions.

    Raises:
        ValueError: If no valid JSON could be recovered.
    """
    candidates = [content.strip()]

    fenced = re.search(r"```(?:json)?\s*(.*?)```", content, re.DOTALL)
    if fenced:
        candidates.append(fenced.group(1).strip())

    block = JSON_BLOCK_PATTERN.search(content)
    if block:
        candidates.append(block.group(1).strip())

    for candidate in candidates:
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            # A bare action dict, or a model that wrapped the list in a key
            # such as {"actions": [...]}.
            if "action" in parsed:
                return [parsed]
            for value in parsed.values():
                if isinstance(value, list):
                    return value
            return [parsed]

    raise ValueError(f"Failed to parse LLM response: {content}")


async def parse_command(command: str) -> list[dict]:
    """
    Sends a user command to the LLM and parses its response into structured actions.

    Args:
        command (str): Natural language instruction.

    Returns:
        list[dict]: List of action dictionaries.

    Raises:
        ValueError: If the LLM response cannot be parsed as valid JSON.
    """
    logger.info(f"Sending prompt to LLM: {command}")

    response = await client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": command},
        ],
    )

    content = response["message"]["content"]
    logger.debug(f"LLM response: {content}")

    try:
        return extract_json(content)
    except ValueError:
        logger.error("LLM response could not be parsed as JSON.")
        raise
