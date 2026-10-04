from __future__ import annotations

from typing import Any
import numpy as np
import torch
from torch.utils.data import DataLoader


@torch.inference_mode()
def evaluate_model(
    model: torch.nn.Module,
    loader: DataLoader,
    device: torch.device,
    classes: tuple[str, ...],
) -> dict[str, Any]:
    model.eval()
    correct = 0
    total = 0
    all_preds = []
    all_targets = []

    for x_batch, y_batch in loader:
        x_batch = x_batch.to(device)
        y_batch = y_batch.to(device)
        outputs = model(x_batch)
        preds = torch.argmax(outputs, dim=-1)

        correct += (preds == y_batch).sum().item()
        total += y_batch.size(0)
        all_preds.extend(preds.cpu().numpy().tolist())
        all_targets.extend(y_batch.cpu().numpy().tolist())

    accuracy = correct / max(total, 1)

    # Compute per-class accuracy
    class_stats = {}
    all_preds_arr = np.array(all_preds)
    all_targets_arr = np.array(all_targets)

    for idx, name in enumerate(classes):
        mask = all_targets_arr == idx
        if np.sum(mask) > 0:
            cls_acc = float(np.mean(all_preds_arr[mask] == all_targets_arr[mask]))
        else:
            cls_acc = 0.0
        class_stats[name] = {"samples": int(np.sum(mask)), "accuracy": cls_acc}

    return {
        "accuracy": accuracy,
        "total_samples": total,
        "classes": class_stats,
    }