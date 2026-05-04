import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    system="You are a senior software engineer doing code review. Be specific, concise, and actionable.",
    messages=[
        {"role": "user", "content": "Review this code:\n\ndef get_user(id):\n    return db.query('SELECT * FROM users WHERE id=' + id)"}
    ]
)

print(response.content[0].text)