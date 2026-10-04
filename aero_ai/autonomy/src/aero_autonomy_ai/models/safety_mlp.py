from __future__ import annotations

import torch
import torch.nn as nn
from aero_autonomy_ai.config import ModelConfig
from aero_autonomy_ai.models.registry import register_model


@register_model("safety_mlp")
class FlightSafetyMLP(nn.Module):
    """Sub-millisecond latency dense network for real-time failsafe classification."""

    def __init__(self, config: ModelConfig) -> None:
        super().__init__()
        layers = []
        prev_dim = config.input_dim

        for hidden_dim in config.hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.ReLU(inplace=True))
            if config.dropout > 0.0:
                layers.append(nn.Dropout(config.dropout))
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, config.num_classes))
        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Accepts [batch, input_dim] or flattened [batch, window * input_dim]
        if x.dim() > 2:
            x = x.flatten(start_dim=1)
        return self.network(x)