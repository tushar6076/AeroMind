from __future__ import annotations

from typing import Callable, Dict
import torch.nn as nn
from aero_autonomy_ai.config import ModelConfig

_AUTONOMY_REGISTRY: Dict[str, Callable[[ModelConfig], nn.Module]] = {}


def register_model(name: str):
    def decorator(fn: Callable[[ModelConfig], nn.Module]):
        _AUTONOMY_REGISTRY[name] = fn
        return fn
    return decorator


def build_model(config: ModelConfig) -> nn.Module:
    arch = config.architecture
    if arch not in _AUTONOMY_REGISTRY:
        raise ValueError(
            f"Unknown autonomy model '{arch}'. Registered: {list(_AUTONOMY_REGISTRY.keys())}"
        )
    return _AUTONOMY_REGISTRY[arch](config)