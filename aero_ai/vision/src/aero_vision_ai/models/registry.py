from __future__ import annotations

from typing import Callable, Dict
import torch.nn as nn

from aero_vision_ai.config import ModelConfig

_DETECTOR_REGISTRY: Dict[str, Callable[[ModelConfig], nn.Module]] = {}


def register_detector(name: str):
    def decorator(fn: Callable[[ModelConfig], nn.Module]):
        _DETECTOR_REGISTRY[name] = fn
        return fn
    return decorator


def build_detector(config: ModelConfig) -> nn.Module:
    arch = config.architecture
    if arch not in _DETECTOR_REGISTRY:
        raise ValueError(
            f"Unknown detector architecture '{arch}'. Available: {list(_DETECTOR_REGISTRY.keys())}"
        )
    return _DETECTOR_REGISTRY[arch](config)