from __future__ import annotations

import torch
import torch.nn as nn
from aero_autonomy_ai.config import ModelConfig
from aero_autonomy_ai.models.registry import register_model


@register_model("temporal_1dcnn")
class Temporal1DCNN(nn.Module):
    """1D Convolutional network to detect motor oscillations & harmonic vibrations."""

    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        self.conv1 = nn.Conv1d(config.input_dim, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(32)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(64)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(64, config.num_classes)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Expected input shape: [batch, input_dim, window_size]
        if x.dim() == 2:
            x = x.unsqueeze(-1)
        elif x.shape[1] != self.conv1.in_channels and x.shape[2] == self.conv1.in_channels:
            x = x.transpose(1, 2)

        x = self.relu(self.bn1(self.conv1(x)))
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.pool(x).flatten(1)
        return self.fc(x)