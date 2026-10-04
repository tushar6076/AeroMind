import numpy as np
import torch
from torch.utils.data import DataLoader

from aero_autonomy_ai.config import ModelConfig
from aero_autonomy_ai.data.dataset import TelemetryDataset
from aero_autonomy_ai.engine.checkpoint import load_checkpoint, save_checkpoint
from aero_autonomy_ai.engine.evaluate import evaluate_model
from aero_autonomy_ai.models.safety_mlp import FlightSafetyMLP


def test_checkpoint_save_and_load(tmp_path):
    cfg = ModelConfig(
        architecture="safety_mlp",
        input_dim=4,
        hidden_dims=(16, 8),
        num_classes=2,
        classes=("nominal", "anomaly"),
        dropout=0.0,
    )
    model = FlightSafetyMLP(cfg)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    ckpt_file = tmp_path / "best.pth"
    save_checkpoint(ckpt_file, model, optimizer, epoch=1, accuracy=0.95, classes=cfg.classes)

    assert ckpt_file.is_file()

    # Load into fresh instance
    new_model = FlightSafetyMLP(cfg)
    loaded_data = load_checkpoint(ckpt_file, new_model, torch.device("cpu"))
    assert loaded_data["epoch"] == 1
    assert loaded_data["accuracy"] == 0.95

    # Parameter equality check
    for p1, p2 in zip(model.parameters(), new_model.parameters()):
        assert torch.equal(p1, p2)


def test_evaluate_model():
    cfg = ModelConfig(
        architecture="safety_mlp",
        input_dim=4,
        hidden_dims=(8,),
        num_classes=2,
        classes=("nominal", "anomaly"),
        dropout=0.0,
    )
    model = FlightSafetyMLP(cfg)
    model.eval()

    # Synthetic batch
    x = np.random.randn(10, 4).astype(np.float32)
    y = np.random.randint(0, 2, size=(10,)).astype(np.int64)
    loader = DataLoader(TelemetryDataset(x, y), batch_size=5)

    metrics = evaluate_model(model, loader, torch.device("cpu"), cfg.classes)
    assert "accuracy" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert "classes" in metrics
    assert "nominal" in metrics["classes"]
    assert "anomaly" in metrics["classes"]