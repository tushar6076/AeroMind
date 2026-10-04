from __future__ import annotations

import torchvision
from torchvision.models.detection.ssd import SSDClassificationHead

from aero_vision_ai.config import ModelConfig
from aero_vision_ai.models.registry import register_detector


@register_detector("ssd_mobilenet_v3")
def build_ssd_mobilenet(config: ModelConfig):
    weights = torchvision.models.detection.SSD300_VGG16_Weights.DEFAULT if config.pretrained else None
    model = torchvision.models.detection.ssdlite320_mobilenet_v3_large(
        weights=None,
        num_classes=len(config.classes) + 1,
    )
    return model