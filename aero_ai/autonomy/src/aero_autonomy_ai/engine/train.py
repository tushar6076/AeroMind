from __future__ import annotations

import random
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from aero_autonomy_ai.config import AutonomyConfig
from aero_autonomy_ai.data import TelemetryDataset, TelemetryNormalizer
from aero_autonomy_ai.engine.checkpoint import save_checkpoint
from aero_autonomy_ai.engine.evaluate import evaluate_model
from aero_autonomy_ai.models import build_model


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def create_synthetic_data(config: AutonomyConfig) -> tuple[DataLoader, DataLoader]:
    """Generates synthetic dataset when no physical flight logs are present."""
    num_samples = 1000
    x = np.random.randn(num_samples, config.model.input_dim).astype(np.float32)
    y = np.random.randint(0, config.model.num_classes, size=(num_samples,)).astype(np.int64)

    norm = TelemetryNormalizer(config.data.features)
    norm.fit(x)
    norm.save(config.root / "artifacts" / "normalization_stats.json")
    x_norm = norm.transform(x)

    split = int(num_samples * (1 - config.data.val_split))
    train_ds = TelemetryDataset(x_norm[:split], y[:split])
    val_ds = TelemetryDataset(x_norm[split:], y[split:])

    return (
        DataLoader(train_ds, batch_size=config.training.batch_size, shuffle=True),
        DataLoader(val_ds, batch_size=config.training.batch_size, shuffle=False),
    )


def train(config: AutonomyConfig, device: torch.device | None = None) -> Path:
    seed_everything(config.training.seed)
    selected_device = device or torch.device(
        "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    )

    train_loader, val_loader = create_synthetic_data(config)
    model = build_model(config.model).to(selected_device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config.training.learning_rate,
        weight_decay=config.training.weight_decay,
    )

    out_dir = config.training.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    best_path = out_dir / "best.pth"
    best_acc = -1.0

    for epoch in range(1, config.training.epochs + 1):
        model.train()
        total_loss = 0.0
        batches = 0

        for x_b, y_b in train_loader:
            x_b, y_b = x_b.to(selected_device), y_b.to(selected_device)
            optimizer.zero_grad()
            out = model(x_b)
            loss = criterion(out, y_b)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            batches += 1

        eval_res = evaluate_model(model, val_loader, selected_device, config.model.classes)
        acc = eval_res["accuracy"]

        if acc > best_acc:
            best_acc = acc
            save_checkpoint(best_path, model, optimizer, epoch, best_acc, config.model.classes)

        if epoch % 10 == 0 or epoch == config.training.epochs:
            print(f"Epoch {epoch:03d} | Loss: {total_loss / max(batches, 1):.4f} | Val Accuracy: {acc * 100:.2f}%")

    print(f"--> Autonomy training complete. Best accuracy: {best_acc * 100:.2f}% saved to {best_path}")
    return best_path