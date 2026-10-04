import torch
from aero_autonomy_ai.config import ModelConfig
from aero_autonomy_ai.models import build_model


def test_safety_mlp_forward():
    cfg = ModelConfig(
        architecture="safety_mlp",
        input_dim=6,
        hidden_dims=(16, 8),
        num_classes=3,
        classes=("c1", "c2", "c3"),
        dropout=0.0,
    )
    model = build_model(cfg)
    model.eval()  # Avoid BatchNorm running stat accumulation during test
    x = torch.randn(4, 6)
    with torch.no_grad():
        out = model(x)
    assert out.shape == (4, 3)


def test_temporal_1dcnn_forward():
    cfg = ModelConfig(
        architecture="temporal_1dcnn",
        input_dim=4,
        hidden_dims=(16,),
        num_classes=2,
        classes=("ok", "err"),
        dropout=0.0,
    )
    model = build_model(cfg)
    model.eval()
    x = torch.randn(4, 4, 16)
    with torch.no_grad():
        out = model(x)
    assert out.shape == (4, 2)