from app.services.ai.core.selector import select_provider
from app.services.ai.core.response import format_ai_response
from app.services.ai.core.information import DRONE_CONTEXT, SYSTEM_ROLE
from app.services.ai import providers


async def identify(
    input_data: dict,
    application: str = "general",
    preferred_provider: str | None = None,
    enhance_with_llm: bool = True
) -> dict:
    """
    Main AI identification entry point.

    Flow:
    1. Select application pipeline (trees / humans / vehicles / general)
    2. Run local model(s)  [to be connected later]
    3. Optionally enhance result using external LLM
    4. Return formatted response
    """

    provider = select_provider(preferred_provider)

    # -------------------------------------------------
    # 1. Local Model Prediction (Placeholder for now)
    # -------------------------------------------------
    # Later this will call applications/trees.py, humans.py etc.
    local_result = {
        "application": application,
        "detection": "pending_local_model",
        "confidence": None,
        "raw": input_data
    }

    # -------------------------------------------------
    # 2. Optional LLM Enhancement
    # -------------------------------------------------
    enhanced_content = None

    if enhance_with_llm and provider != "local":
        prompt = f"""
{SYSTEM_ROLE}

Context:
{DRONE_CONTEXT}

Application: {application}
Local Detection Result: {local_result}

Based on the detection, provide a clear and useful explanation or recommendation.
"""

        try:
            if provider == "groq":
                enhanced_content = await providers.groq.generate(prompt)
            elif provider == "gemini":
                enhanced_content = await providers.gemini.generate(prompt)
            elif provider == "openai":
                enhanced_content = await providers.openai.generate(prompt)
            elif provider == "grok":
                enhanced_content = await providers.grok.generate(prompt)
            else:
                enhanced_content = "No external provider available."
        except Exception as e:
            enhanced_content = f"LLM enhancement failed: {str(e)}"

    # -------------------------------------------------
    # 3. Final Response
    # -------------------------------------------------
    return format_ai_response(
        content=enhanced_content or "Local detection only",
        provider=provider,
        model=application,
        success=True,
        extra={
            "local_result": local_result
        }
    )