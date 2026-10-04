from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from PIL import Image
from torchvision.transforms import functional as TF

from aero_vision_ai.config import AppConfig
from aero_vision_ai.engine.checkpoint import load_checkpoint
from aero_vision_ai.models import build_detector


def load_model(
    config: AppConfig,
    checkpoint_path: str | Path,
    device: torch.device | None = None,
) -> tuple[torch.nn.Module, torch.device]:
    selected_device = device or torch.device(
        "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    )
    model = build_detector(config.model).to(selected_device)
    load_checkpoint(checkpoint_path, model, config.model.classes, selected_device)
    model.eval()
    return model, selected_device


@torch.inference_mode()
def predict_image(
    model: torch.nn.Module,
    image_path: str | Path,
    class_names: tuple[str, ...],
    device: torch.device,
    score_threshold: float,
) -> dict[str, Any]:
    source = Path(image_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Image not found: {source}")

    with Image.open(source) as image_file:
        image = image_file.convert("RGB")
        width, height = image.size
        tensor = TF.pil_to_tensor(image).to(torch.float32) / 255.0

    result = model([tensor.to(device)])[0]
    detections = []
    for box, label, score in zip(result["boxes"], result["labels"], result["scores"]):
        conf = float(score.cpu())
        if conf < score_threshold:
            continue
        class_id = int(label.cpu())
        detections.append(
            {
                "class_id": class_id,
                "class_name": class_names[class_id - 1],
                "score": conf,
                "bbox_xyxy": [float(v) for v in box.cpu().tolist()],
            }
        )

    return {
        "image": str(source),
        "width": width,
        "height": height,
        "detections": detections,
    }