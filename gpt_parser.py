from ollama import Client

client = Client(host='http://localhost:11434')

async def parse_command(command: str) -> dict:
    response = client.chat(
        model='mistral',
        messages=[
            {"role": "system", "content": "Translate natural language browser commands into structured JSON actions like: {\"action\": \"search\", \"site\": \"https://www.youtube.com\", \"query\": \"cats\"}"},
            {"role": "user", "content": command},
        ]
    )

    content = response['message']['content']
    import json
    return json.loads(content)
