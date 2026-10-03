from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.intelligence import AIModel


async def seed_ai_models(db: AsyncSession) -> None:
    seed_models_data = [
        {
            "name": "Human Analytics Engine",
            "key": "human_analytics",
            "description": "Multi-stage computer vision model for human detection, demographics, and posture analysis.",
            "levels": ["detection", "gender_age", "posture_activity"],
            "provider": "local",
            "is_active": True,
        },
        {
            "name": "Aerial Canopy & Tree Counter",
            "key": "tree_canopy",
            "description": "High-resolution segmentation model specialized for forestry and agricultural land surveying.",
            "levels": ["canopy_segmentation", "tree_count", "health_index"],
            "provider": "local",
            "is_active": True,
        },
        {
            "name": "Gemini 1.5 Pro Aerial Intelligence",
            "key": "gemini_aerial_vision",
            "description": "Multimodal visual reasoning for contextual drone feed analysis and automated reporting.",
            "levels": ["zero_shot_classification", "scene_description", "threat_assessment"],
            "provider": "gemini",
            "is_active": True,
        },
        {
            "name": "Groq LLaMA3 Flight Assistant",
            "key": "groq_llama3_pilot",
            "description": "Ultra-low latency LLM for processing real-time telemetry logs and pilot query routing.",
            "levels": ["telemetry_parsing", "route_optimization"],
            "provider": "groq",
            "is_active": False,
        },
    ]

    for model_data in seed_models_data:
        result = await db.execute(select(AIModel).where(AIModel.key == model_data["key"]))
        existing_model = result.scalars().first()

        if not existing_model:
            model = AIModel(
                name=model_data["name"],
                key=model_data["key"],
                description=model_data["description"],
                levels=model_data["levels"],
                provider=model_data["provider"],
                is_active=model_data["is_active"],
            )
            db.add(model)
            print(f"[SEED] Created AI model: {model.name} (Key: {model.key}, Provider: {model.provider})")
        else:
            print(f"[SEED] Skipping existing AI model: {model_data['key']}")

    await db.commit()