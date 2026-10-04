from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import torch

from aero_autonomy_ai.config import AutonomyConfig
from aero_autonomy_ai.data.normalizer import TelemetryNormalizer
from aero_autonomy_ai.engine.checkpoint import load_checkpoint
from aero_autonomy_ai.models import build_model


def load_inference_model(
    config: AutonomyConfig,
    checkpoint_path: str | Path,
    device: torch.device | None = None,
) -> tuple[torch.nn.Module, torch.device]:
    """Instantiate and load model weights for evaluation or deployment."""
    selected_device = device or torch.device(
        "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    )
    model = build_model(config.model).to(selected_device)
    load_checkpoint(checkpoint_path, model, selected_device)
    model.eval()
    return model, selected_device


@torch.inference_mode()
def predict_telemetry_vector(
    model: torch.nn.Module,
    vector: list[float] | np.ndarray,
    normalizer: TelemetryNormalizer | None,
    class_names: tuple[str, ...],
    device: torch.device,
) -> dict[str, Any]:
    """Run inference on a single instantaneous telemetry reading."""
    arr = np.asarray(vector, dtype=np.float32).reshape(1, -1)
    if normalizer is not None:
        arr = normalizer.transform(arr)

    tensor = torch.from_numpy(arr).to(device)
    logits = model(tensor)
    probs = torch.softmax(logits, dim=-1).squeeze(0).cpu().numpy()
    pred_idx = int(np.argmax(probs))

    return {
        "predicted_class_id": pred_idx,
        "predicted_label": class_names[pred_idx],
        "confidence": float(probs[pred_idx]),
        "probabilities": {class_names[i]: float(p) for i, p in enumerate(probs)},
    }


@torch.inference_mode()
def predict_telemetry_batch(
    model: torch.nn.Module,
    matrix: np.ndarray,
    normalizer: TelemetryNormalizer | None,
    class_names: tuple[str, ...],
    device: torch.device,
) -> list[dict[str, Any]]:
    """Run batched inference over a sequence or window of telemetry frames."""
    arr = np.asarray(matrix, dtype=np.float32)
    if normalizer is not None:
        arr = normalizer.transform(arr)

    tensor = torch.from_numpy(arr).to(device)
    logits = model(tensor)
    probs = torch.softmax(logits, dim=-1).cpu().numpy()
    pred_indices = np.argmax(probs, axis=-1)

    results = []
    for idx, p_dist in zip(pred_indices, probs):
        results.append(
            {
                "predicted_class_id": int(idx),
                "predicted_label": class_names[idx],
                "confidence": float(p_dist[idx]),
                "probabilities": {class_names[i]: float(p) for i, p in enumerate(p_dist)},
            }
        )
    return results