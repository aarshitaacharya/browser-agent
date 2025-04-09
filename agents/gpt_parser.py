import json
from ollama import Client
from utils.logger import logger

# Initialize LLM client
client = Client(host="http://localhost:11434")

def load_prompt_examples(file_path: str = "prompts/prompt_examples.txt") -> str:
    """
    Loads prompt examples from a text file to prime the LLM.

    Args:
        file_path (str): Path to the prompt examples file.

    Returns:
        str: Prompt examples as a single string.
    """
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Prompt examples file not found at path: {file_path}")
        return ""


# Static system prompt (few-shot instructions + examples)
SYSTEM_PROMPT = (
    "You are a browser automation agent.\n"
    "Translate user commands into a JSON array of actions.\n"
    "Use only the following action types:\n"
    "- goto\n- fill\n- click\n- keyboard_press\n- wait\n\n"
    "Each action should be a dictionary. Only return the JSON array.\n\n"
    + load_prompt_examples()
)


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

    response = client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": command},
        ]
    )

    content = response["message"]["content"]
    logger.debug(f"LLM response: {content}")

    try:
        actions = json.loads(content)
        if isinstance(actions, dict):
            actions = [actions]
        return actions
    except json.JSONDecodeError:
        logger.error("LLM response could not be parsed as JSON.")
        raise ValueError(f"Failed to parse LLM response: {content}")
