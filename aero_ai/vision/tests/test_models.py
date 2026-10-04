import torch
from aero_vision_ai.config import ModelConfig
from aero_vision_ai.models import build_detector


def test_model_registry_build():
    cfg = ModelConfig(
        architecture="faster_rcnn_resnet50",
        classes=("person", "vehicle", "animal"),
        pretrained=False,
        trainable_backbone_layers=5,
        min_size=640,
        max_size=640,
        anchor_sizes=(32, 64),
        aspect_ratios=(1.0,),
    )
    model = build_detector(cfg)
    assert isinstance(model, torch.nn.Module)