from groq import Groq
from app.core.config import settings
import json

def get_client():
    return Groq(api_key=settings.GEMINI_API_KEY)

async def summarize_note(title: str, content: str) -> str:
    if not content.strip():
        return ""
    client = get_client()
    chat = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"Summarize this note in 2-3 sentences only:\n\nTitle: {title}\n\nContent: {content}"}],
        max_tokens=200
    )
    return chat.choices[0].message.content.strip()

async def generate_tags(title: str, content: str) -> list[str]:
    if not content.strip():
        return []
    client = get_client()
    chat = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": f"Generate 3-5 tags for this note. Return ONLY a JSON array like [\"tag1\",\"tag2\"]. No explanation.\n\nTitle: {title}\n\nContent: {content}"}],
        max_tokens=100
    )
    raw = chat.choices[0].message.content.strip()
    try:
        return json.loads(raw)[:5]
    except:
        return ["note", "ai", "summary"]