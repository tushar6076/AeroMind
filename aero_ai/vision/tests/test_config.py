import pytest
from aero_vision_ai.config import load_config


def test_load_config_success(tmp_path):
    cfg_file = tmp_path / "detection.yaml"
    cfg_file.write_text(
        """
data:
  train_images: data/raw/images/train
  train_annotations: data/raw/annotations/train.json
  val_images: data/raw/images/val
  val_annotations: data/raw/annotations/val.json
model:
  architecture: faster_rcnn_resnet50
  classes: [person, vehicle, animal]
  pretrained: false
  trainable_backbone_layers: 1
  min_size: 640
  max_size: 1024
  anchor_sizes: [32, 64]
  aspect_ratios: [0.5, 1.0]
training:
  output_dir: checkpoints
  epochs: 1
  batch_size: 1
  num_workers: 0
  learning_rate: 0.001
  momentum: 0.9
  weight_decay: 0.0001
  step_size: 5
  gamma: 0.1
  score_threshold: 0.3
  seed: 42
  horizontal_flip_probability: 0.5
evaluation:
  iou_thresholds: [0.5]
  score_threshold: 0.3
export:
  input_size: 640
  opset: 17
  max_detections: 50
""",
        encoding="utf-8",
    )
    config = load_config(cfg_file)
    assert config.model.architecture == "faster_rcnn_resnet50"
    assert config.model.classes == ("person", "vehicle", "animal")