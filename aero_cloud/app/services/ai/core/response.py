def format_ai_response(
    content: str,
    provider: str,
    model: str | None = None,
    success: bool = True,
    extra: dict | None = None
) -> dict:
    return {
        "success": success,
        "provider": provider,
        "model": model,
        "content": content,
        "extra": extra or {}
    }