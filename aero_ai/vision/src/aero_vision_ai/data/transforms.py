from __future__ import annotations

import random
import torch


class DetectionHorizontalFlip:
    """Synchronized horizontal flip for image tensor and bounding boxes."""

    def __init__(self, probability: float = 0.5) -> None:
        self.probability = probability

    def __call__(
        self, image: torch.Tensor, target: dict[str, torch.Tensor], width: int
    ) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
        if random.random() < self.probability:
            image = image.flip(-1)
            boxes = target["boxes"]
            if boxes.numel() > 0:
                old_left = boxes[:, 0].clone()
                boxes[:, 0] = width - boxes[:, 2]
                boxes[:, 2] = width - old_left
                target["boxes"] = boxes
        return image, target