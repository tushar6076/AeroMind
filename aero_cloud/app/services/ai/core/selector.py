from app.core.config import settings

def select_provider(preferred: str | None = None) -> str:
    if preferred:
        return preferred.lower()

    if settings.GROQ_API_KEY:
        return "groq"
    if settings.GEMINI_API_KEY:
        return "gemini"
    if settings.OPENAI_API_KEY:
        return "openai"
    if settings.GROK_API_KEY:
        return "grok"
    return "local"