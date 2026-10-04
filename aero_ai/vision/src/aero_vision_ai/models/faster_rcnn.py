from __future__ import annotations

from torchvision.models.detection import (
    FasterRCNN_ResNet50_FPN_Weights,
    fasterrcnn_resnet50_fpn,
)
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.rpn import AnchorGenerator

from aero_vision_ai.config import ModelConfig
from aero_vision_ai.models.registry import register_detector


@register_detector("faster_rcnn_resnet50")
def build_faster_rcnn(config: ModelConfig):
    weights = FasterRCNN_ResNet50_FPN_Weights.DEFAULT if config.pretrained else None
    
    # Passing None when unweighted tells torchvision to default to all trainable without emitting a warning
    trainable_layers = config.trainable_backbone_layers if config.pretrained else None

    model = fasterrcnn_resnet50_fpn(
        weights=weights,
        weights_backbone=None,
        trainable_backbone_layers=trainable_layers,
        min_size=config.min_size,
        max_size=config.max_size,
        rpn_anchor_generator=AnchorGenerator(
            sizes=(config.anchor_sizes,) * 5,
            aspect_ratios=(config.aspect_ratios,) * 5,
        ),
    )
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # Number of configured classes + 1 background class (id 0)
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, len(config.classes) + 1)
    return model