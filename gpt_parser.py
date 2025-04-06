from ollama import Client

client = Client(host='http://localhost:11434')

# Load your prompt examples from a file
with open("prompts/prompt_examples.txt", "r") as f:
    prompt_examples = f.read()

# System prompt (prefix + examples)
SYSTEM_PROMPT = (
    "You are a browser automation agent.\n"
    "Translate user commands into a JSON array of actions.\n"
    "Use only the following action types:\n"
    "- goto\n- fill\n- click\n- keyboard_press\n- wait\n\n"
    "Each action should be a dictionary. Only return the JSON array.\n\n"
    + prompt_examples
)

async def parse_command(command: str) -> list:
    response = client.chat(
        model='mistral',
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": command},
        ]
    )

    content = response['message']['content']

    import json
    try:
        actions = json.loads(content)
        if isinstance(actions, dict):
            actions = [actions]
        return actions
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse LLM response: {content}")
