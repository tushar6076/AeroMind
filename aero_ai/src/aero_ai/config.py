from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DataConfig:
    train_images: Path
    train_annotations: Path
    val_images: Path
    val_annotations: Path


@dataclass(frozen=True)
class ModelConfig:
    classes: tuple[str, ...]
    pretrained: bool
    trainable_backbone_layers: int
    min_size: int
    max_size: int
    anchor_sizes: tuple[int, ...]
    aspect_ratios: tuple[float, ...]


@dataclass(frozen=True)
class TrainingConfig:
    output_dir: Path
    epochs: int
    batch_size: int
    num_workers: int
    learning_rate: float
    momentum: float
    weight_decay: float
    step_size: int
    gamma: float
    score_threshold: float
    seed: int
    horizontal_flip_probability: float


@dataclass(frozen=True)
class EvaluationConfig:
    iou_thresholds: tuple[float, ...]
    score_threshold: float


@dataclass(frozen=True)
class ExportConfig:
    input_size: int
    opset: int
    max_detections: int


@dataclass(frozen=True)
class AppConfig:
    root: Path
    data: DataConfig
    model: ModelConfig
    training: TrainingConfig
    evaluation: EvaluationConfig
    export: ExportConfig


def _required(mapping: dict[str, Any], key: str, section: str) -> Any:
    if key not in mapping:
        raise ValueError(f"Missing required configuration key: {section}.{key}")
    return mapping[key]


def _resolve(root: Path, value: str, key: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Configuration path '{key}' must be a non-empty string.")
    path = Path(value).expanduser()
    return (root / path).resolve() if not path.is_absolute() else path.resolve()


def load_config(config_path: str | Path) -> AppConfig:
    config_file = Path(config_path).expanduser().resolve()
    if not config_file.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with config_file.open("r", encoding="utf-8") as stream:
        raw = yaml.safe_load(stream)
    if not isinstance(raw, dict):
        raise ValueError("Configuration must be a YAML mapping.")

    root = Path.cwd().resolve()
    data_raw = _required(raw, "data", "root")
    model_raw = _required(raw, "model", "root")
    training_raw = _required(raw, "training", "root")
    evaluation_raw = _required(raw, "evaluation", "root")
    export_raw = _required(raw, "export", "root")

    classes = tuple(str(name).strip() for name in _required(model_raw, "classes", "model"))
    if not classes or any(not name for name in classes):
        raise ValueError("model.classes must contain at least one non-empty class name.")
    if len(set(classes)) != len(classes):
        raise ValueError("model.classes must not contain duplicate names.")

    model = ModelConfig(
        classes=classes,
        pretrained=bool(_required(model_raw, "pretrained", "model")),
        trainable_backbone_layers=int(
            _required(model_raw, "trainable_backbone_layers", "model")
        ),
        min_size=int(_required(model_raw, "min_size", "model")),
        max_size=int(_required(model_raw, "max_size", "model")),
        anchor_sizes=tuple(int(value) for value in _required(model_raw, "anchor_sizes", "model")),
        aspect_ratios=tuple(
            float(value) for value in _required(model_raw, "aspect_ratios", "model")
        ),
    )
    training = TrainingConfig(
        output_dir=_resolve(
            root, _required(training_raw, "output_dir", "training"), "training.output_dir"
        ),
        epochs=int(_required(training_raw, "epochs", "training")),
        batch_size=int(_required(training_raw, "batch_size", "training")),
        num_workers=int(_required(training_raw, "num_workers", "training")),
        learning_rate=float(_required(training_raw, "learning_rate", "training")),
        momentum=float(_required(training_raw, "momentum", "training")),
        weight_decay=float(_required(training_raw, "weight_decay", "training")),
        step_size=int(_required(training_raw, "step_size", "training")),
        gamma=float(_required(training_raw, "gamma", "training")),
        score_threshold=float(_required(training_raw, "score_threshold", "training")),
        seed=int(_required(training_raw, "seed", "training")),
        horizontal_flip_probability=float(
            _required(training_raw, "horizontal_flip_probability", "training")
        ),
    )
    evaluation = EvaluationConfig(
        iou_thresholds=tuple(
            float(value) for value in _required(evaluation_raw, "iou_thresholds", "evaluation")
        ),
        score_threshold=float(_required(evaluation_raw, "score_threshold", "evaluation")),
    )
    export = ExportConfig(
        input_size=int(_required(export_raw, "input_size", "export")),
        opset=int(_required(export_raw, "opset", "export")),
        max_detections=int(_required(export_raw, "max_detections", "export")),
    )
    config = AppConfig(
        root=root,
        data=DataConfig(
            train_images=_resolve(
                root, _required(data_raw, "train_images", "data"), "data.train_images"
            ),
            train_annotations=_resolve(
                root,
                _required(data_raw, "train_annotations", "data"),
                "data.train_annotations",
            ),
            val_images=_resolve(root, _required(data_raw, "val_images", "data"), "data.val_images"),
            val_annotations=_resolve(
                root, _required(data_raw, "val_annotations", "data"), "data.val_annotations"
            ),
        ),
        model=model,
        training=training,
        evaluation=evaluation,
        export=export,
    )
    validate_config(config)
    return config


def validate_config(config: AppConfig) -> None:
    if config.model.trainable_backbone_layers not in range(0, 6):
        raise ValueError("model.trainable_backbone_layers must be between 0 and 5.")
    if config.model.min_size <= 0 or config.model.max_size < config.model.min_size:
        raise ValueError("model image sizes must be positive and max_size >= min_size.")
    if not config.model.anchor_sizes or any(size <= 0 for size in config.model.anchor_sizes):
        raise ValueError("model.anchor_sizes must contain positive values.")
    if not config.model.aspect_ratios or any(ratio <= 0 for ratio in config.model.aspect_ratios):
        raise ValueError("model.aspect_ratios must contain positive values.")
    if config.training.epochs <= 0 or config.training.batch_size <= 0:
        raise ValueError("training.epochs and training.batch_size must be positive.")
    if config.training.num_workers < 0:
        raise ValueError("training.num_workers cannot be negative.")
    if config.training.learning_rate <= 0 or config.training.weight_decay < 0:
        raise ValueError("training.learning_rate must be positive and weight_decay non-negative.")
    if config.training.step_size <= 0 or not 0 < config.training.gamma <= 1:
        raise ValueError("training.step_size must be positive and gamma must be in (0, 1].")
    for name, threshold in (
        ("training.score_threshold", config.training.score_threshold),
        ("evaluation.score_threshold", config.evaluation.score_threshold),
    ):
        if not 0 <= threshold <= 1:
            raise ValueError(f"{name} must be between 0 and 1.")
    if not 0 <= config.training.horizontal_flip_probability <= 1:
        raise ValueError("training.horizontal_flip_probability must be between 0 and 1.")
    if not config.evaluation.iou_thresholds or any(
        not 0 < threshold <= 1 for threshold in config.evaluation.iou_thresholds
    ):
        raise ValueError("evaluation.iou_thresholds must contain values in (0, 1].")
    if config.export.input_size <= 0 or config.export.max_detections <= 0:
        raise ValueError("export.input_size and export.max_detections must be positive.")
