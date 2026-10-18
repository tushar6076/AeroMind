from app.schemas.ai import AIInventory, AIModelSummary


class AIService:
    def inventory(self) -> AIInventory:
        return AIInventory(
            mode="demo",
            note="Backend demo catalog only; model inference is not connected.",
            models=[
                AIModelSummary(
                    name="AeroVision Object Detector",
                    version="demo",
                    task="Object detection",
                    status="Simulated",
                ),
                AIModelSummary(
                    name="AeroMind Scene Classifier",
                    version="demo",
                    task="Scene classification",
                    status="Simulated",
                ),
            ],
        )