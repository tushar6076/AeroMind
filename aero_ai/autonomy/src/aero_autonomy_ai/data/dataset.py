from __future__ import annotations

import numpy as np
import torch
from torch.utils.data import Dataset


class TelemetryDataset(Dataset):
    """In-memory dataset for tabular or windowed telemetry tensors."""

    def __init__(self, x_data: np.ndarray, y_data: np.ndarray) -> None:
        self.x = torch.from_numpy(x_data.astype(np.float32))
        self.y = torch.from_numpy(y_data.astype(np.int64))

    def __len__(self) -> int:
        return len(self.x)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.x[idx], self.y[idx]