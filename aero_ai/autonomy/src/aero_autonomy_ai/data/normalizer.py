from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import numpy as np


class TelemetryNormalizer:
    """Computes and applies per-feature mean and std scaling for telemetry inputs."""

    def __init__(self, features: tuple[str, ...]) -> None:
        self.features = features
        self.mean: np.ndarray | None = None
        self.std: np.ndarray | None = None

    def fit(self, data: np.ndarray) -> None:
        self.mean = np.mean(data, axis=0)
        self.std = np.std(data, axis=0)
        self.std[self.std < 1e-6] = 1.0  # Avoid div by zero

    def transform(self, data: np.ndarray) -> np.ndarray:
        if self.mean is None or self.std is None:
            raise RuntimeError("Normalizer has not been fitted.")
        return (data - self.mean) / self.std

    def save(self, output_path: str | Path) -> None:
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        stats = {
            "features": list(self.features),
            "mean": self.mean.tolist() if self.mean is not None else [],
            "std": self.std.tolist() if self.std is not None else [],
        }
        path.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, stats_path: str | Path) -> TelemetryNormalizer:
        path = Path(stats_path).resolve()
        data = json.loads(path.read_text(encoding="utf-8"))
        norm = cls(tuple(data["features"]))
        norm.mean = np.array(data["mean"], dtype=np.float32)
        norm.std = np.array(data["std"], dtype=np.float32)
        return norm