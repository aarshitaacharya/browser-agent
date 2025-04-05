from ollama import Client
import json

client = Client(host="http://localhost:11434")

# Load prompt examples
with open("prompts/prompt_examples.txt", "r") as f:
    prompt_examples = f.read()

SYSTEM_PROMPT = (
    "You are a browser automation agent.\n"
    "Translate user commands into a JSON array of actions.\n"
    "Use only the following action types:\n"
    "- goto\n- fill\n- click\n- keyboard_press\n\n"
    "Each action must be a dictionary with relevant fields.\n"
    "Return only the raw JSON array — no explanation.\n\n"
    + prompt_examples
)

async def parse_command(command: str) -> list[dict]:
    try:
        response = client.chat(
            model="mistral",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": command},
            ],
        )

        content = response["message"]["content"].strip()

        # Try to extract JSON array
        if not content.startswith("["):
            content = content[content.find("[") :]

        actions = json.loads(content)
        return actions if isinstance(actions, list) else [actions]

    except json.JSONDecodeError:
        raise ValueError(f"❌ Failed to parse LLM response:\n\n{content}")
    except Exception as e:
        raise RuntimeError(f"❌ LLM call failed: {str(e)}")
