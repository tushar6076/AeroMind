from __future__ import annotations

from pathlib import Path
from typing import Any
import torch


def save_checkpoint(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    accuracy: float,
    classes: tuple[str, ...],
) -> None:
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "epoch": epoch,
            "accuracy": accuracy,
            "classes": list(classes),
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
        },
        target,
    )


def load_checkpoint(
    path: str | Path,
    model: torch.nn.Module,
    device: torch.device,
) -> dict[str, Any]:
    target = Path(path).resolve()
    if not target.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {target}")
    checkpoint = torch.load(target, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state_dict"])
    return checkpoint