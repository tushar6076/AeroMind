from __future__ import annotations

from pathlib import Path
from typing import Any

import torch


def save_checkpoint(
    path: str | Path,
    *,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    epoch: int,
    best_map: float,
    class_names: tuple[str, ...],
) -> None:
    checkpoint = {
        "format_version": 1,
        "epoch": epoch,
        "best_map": best_map,
        "class_names": list(class_names),
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "scheduler_state_dict": scheduler.state_dict(),
    }
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(checkpoint, output_path)


def load_checkpoint(
    path: str | Path,
    model: torch.nn.Module,
    class_names: tuple[str, ...],
    device: torch.device,
) -> dict[str, Any]:
    checkpoint_path = Path(path)
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
    state_dict = checkpoint.get("model_state_dict", checkpoint)
    saved_classes = checkpoint.get("class_names")
    if saved_classes is not None and tuple(saved_classes) != class_names:
        raise ValueError(
            f"Checkpoint classes {tuple(saved_classes)} do not match configured classes {class_names}."
        )
    model.load_state_dict(state_dict)
    return checkpoint