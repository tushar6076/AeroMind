from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml


@dataclass(frozen=True)
class DataConfig:
    raw_dir: Path
    processed_dir: Path
    features: tuple[str, ...]
    window_size: int
    stride: int
    val_split: float


@dataclass(frozen=True)
class ModelConfig:
    architecture: str
    input_dim: int
    hidden_dims: tuple[int, ...]
    num_classes: int
    classes: tuple[str, ...]
    dropout: float


@dataclass(frozen=True)
class TrainingConfig:
    output_dir: Path
    epochs: int
    batch_size: int
    learning_rate: float
    weight_decay: float
    seed: int


@dataclass(frozen=True)
class ExportConfig:
    target_format: str
    c_array_name: str
    quantize_calibration_samples: int


@dataclass(frozen=True)
class AutonomyConfig:
    root: Path
    data: DataConfig
    model: ModelConfig
    training: TrainingConfig
    export: ExportConfig


def load_config(config_path: str | Path) -> AutonomyConfig:
    path = Path(config_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as stream:
        raw = yaml.safe_load(stream)

    root = path.parent.parent

    d = raw["data"]
    m = raw["model"]
    t = raw["training"]
    e = raw["export"]

    return AutonomyConfig(
        root=root,
        data=DataConfig(
            raw_dir=(root / d["raw_dir"]).resolve(),
            processed_dir=(root / d["processed_dir"]).resolve(),
            features=tuple(d["features"]),
            window_size=int(d.get("window_size", 16)),
            stride=int(d.get("stride", 4)),
            val_split=float(d.get("val_split", 0.2)),
        ),
        model=ModelConfig(
            architecture=str(m["architecture"]).strip(),
            input_dim=int(m["input_dim"]),
            hidden_dims=tuple(int(v) for v in m.get("hidden_dims", (64, 32))),
            num_classes=int(m["num_classes"]),
            classes=tuple(m["classes"]),
            dropout=float(m.get("dropout", 0.0)),
        ),
        training=TrainingConfig(
            output_dir=(root / t["output_dir"]).resolve(),
            epochs=int(t["epochs"]),
            batch_size=int(t["batch_size"]),
            learning_rate=float(t["learning_rate"]),
            weight_decay=float(t.get("weight_decay", 0.0001)),
            seed=int(t.get("seed", 42)),
        ),
        export=ExportConfig(
            target_format=str(e["target_format"]),
            c_array_name=str(e["c_array_name"]),
            quantize_calibration_samples=int(e.get("quantize_calibration_samples", 200)),
        ),
    )