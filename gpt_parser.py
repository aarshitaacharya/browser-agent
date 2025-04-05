from ollama import Client
import json

client = Client(host='http://localhost:11434')

async def parse_command(command: str) -> list:
    response = client.chat(
        model='mistral',
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a browser automation agent. "
                    "Translate a natural language command into a JSON array of steps. "
                    "Each step should be an object with one of the following actions: 'goto', 'search', 'click', 'fill', 'login'.\n\n"
                    "Only return a raw JSON array. No explanation.\n\n"
                    "Example:\n"
                    "Input: Search for cute puppies on YouTube\n"
                    "Output: [\n"
                    "  {\"action\": \"goto\", \"url\": \"https://www.youtube.com\"},\n"
                    "  {\"action\": \"search\", \"query\": \"cute puppies\"}\n"
                    "]"
                    "Input: Click the first video\n"
                    "Output: {\"action\": \"click\", \"selector\": \"ytd-video-renderer a#thumbnail\"}\n"
                    "Input: Log into the-internet.herokuapp.com with email tomsmith and password SuperSecretPassword!\n"
                    "Output: [\n"
                    "  {\"action\": \"goto\", \"url\": \"https://the-internet.herokuapp.com/login\"},\n"
                    "  {\"action\": \"fill\", \"selector\": \"#username\", \"value\": \"tomsmith\"},\n"
                    "  {\"action\": \"fill\", \"selector\": \"#password\", \"value\": \"SuperSecretPassword!\"},\n"
                    "  {\"action\": \"click\", \"selector\": \"button[type='submit']\"}\n"
                    "]"
                )
            },
            {"role": "user", "content": command},
        ]
    )

    content = response['message']['content']

    try:
        actions = json.loads(content)
        if isinstance(actions, dict):  # fallback in case it's a single object
            actions = [actions]
        return actions
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse LLM response: {content}")