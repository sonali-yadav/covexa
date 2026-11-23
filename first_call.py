import os

from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Client()

response = client.messages.create(
    model = os.getenv("CLAUDE_MODEL", 'claude-haiku-5-5'),
    max_tokens = 15,
    system = "You are a friendly insurance explainer. Answer in 3 sentences.",
    messages = [
        {
            "role": "user",
            "content": "What is a policy endorsement?"
        }
    ],
)

print(response.content[0].text)
print("stop_reason:", response.stop_reason)
print("usage:", response.usage)