from pathlib import Path

import pytest

from aero_ai.config import load_config


ROOT = Path(__file__).resolve().parents[1]


def test_detection_config_resolves_paths_and_classes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(ROOT)
    config = load_config(ROOT / "src" / "aero_ai" / "configs" / "detection.yaml")

    assert config.model.classes == ("person", "vehicle", "animal")
    assert config.data.train_annotations == ROOT / "data/raw/annotations/train.json"
    assert config.training.output_dir == ROOT / "artifacts"


def test_config_rejects_duplicate_class_names(tmp_path: Path) -> None:
    config_path = tmp_path / "detection.yaml"
    config_path.parent.mkdir()
    config_path.write_text(
        """\
data: {train_images: train, train_annotations: train.json, val_images: val, val_annotations: val.json}
model: {classes: [person, person], pretrained: false, trainable_backbone_layers: 3, min_size: 640, max_size: 640, anchor_sizes: [16], aspect_ratios: [1.0]}
training: {output_dir: artifacts, epochs: 1, batch_size: 1, num_workers: 0, learning_rate: 0.001, momentum: 0.9, weight_decay: 0.0005, step_size: 1, gamma: 0.1, score_threshold: 0.25, seed: 1, horizontal_flip_probability: 0.5}
evaluation: {iou_thresholds: [0.5], score_threshold: 0.25}
export: {input_size: 640, opset: 17, max_detections: 100}
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate"):
        load_config(config_path)
