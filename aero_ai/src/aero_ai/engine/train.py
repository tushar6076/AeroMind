from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from aero_ai.config import AppConfig
from aero_ai.data import CocoDetectionDataset, collate_detections
from aero_ai.engine.evaluate import evaluate_model
from aero_ai.models import build_detector
from aero_ai.utils.checkpoint import save_checkpoint


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_loaders(config: AppConfig) -> tuple[DataLoader, DataLoader]:
    train_dataset = CocoDetectionDataset(
        config.data.train_images,
        config.data.train_annotations,
        config.model.classes,
        augment=True,
        horizontal_flip_probability=config.training.horizontal_flip_probability,
    )
    val_dataset = CocoDetectionDataset(
        config.data.val_images,
        config.data.val_annotations,
        config.model.classes,
    )
    if not len(train_dataset) or not len(val_dataset):
        raise ValueError("Both training and validation datasets must contain images.")
    options = {
        "batch_size": config.training.batch_size,
        "num_workers": config.training.num_workers,
        "collate_fn": collate_detections,
        "pin_memory": torch.cuda.is_available(),
    }
    return (
        DataLoader(train_dataset, shuffle=True, **options),
        DataLoader(val_dataset, shuffle=False, **options),
    )


def train(config: AppConfig, device: torch.device | None = None) -> Path:
    seed_everything(config.training.seed)
    selected_device = device or torch.device(
        "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    )
    train_loader, val_loader = build_loaders(config)
    model = build_detector(config.model).to(selected_device)
    optimizer = torch.optim.SGD(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=config.training.learning_rate,
        momentum=config.training.momentum,
        weight_decay=config.training.weight_decay,
    )
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer, step_size=config.training.step_size, gamma=config.training.gamma
    )

    output_dir = config.training.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    best_path = output_dir / "best.pt"
    last_path = output_dir / "last.pt"
    best_map = -1.0

    for epoch in range(1, config.training.epochs + 1):
        model.train()
        running_loss = 0.0
        batches = 0
        progress = tqdm(train_loader, desc=f"Epoch {epoch}/{config.training.epochs}")
        for images, targets in progress:
            images = [image.to(selected_device) for image in images]
            targets = [
                {key: value.to(selected_device) for key, value in target.items()}
                for target in targets
            ]
            optimizer.zero_grad(set_to_none=True)
            loss_dict = model(images, targets)
            losses = sum(loss for loss in loss_dict.values())
            if not torch.isfinite(losses):
                raise FloatingPointError(f"Non-finite training loss at epoch {epoch}: {loss_dict}")
            losses.backward()
            optimizer.step()
            running_loss += float(losses.detach())
            batches += 1
            progress.set_postfix(loss=f"{float(losses.detach()):.4f}")

        scheduler.step()
        metrics = evaluate_model(
            model,
            val_loader,
            selected_device,
            config.model.classes,
            config.evaluation.iou_thresholds,
            config.evaluation.score_threshold,
        )
        epoch_loss = running_loss / max(batches, 1)
        print(
            f"Epoch {epoch:03d} | loss={epoch_loss:.4f} | "
            f"mAP={metrics['map']:.4f} | mAP50={metrics['map50']}"
        )

        save_checkpoint(
            last_path,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            epoch=epoch,
            best_map=max(best_map, float(metrics["map"])),
            class_names=config.model.classes,
        )
        if float(metrics["map"]) > best_map:
            best_map = float(metrics["map"])
            save_checkpoint(
                best_path,
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                epoch=epoch,
                best_map=best_map,
                class_names=config.model.classes,
            )
            print(f"Saved best checkpoint: {best_path}")

    print(f"Training complete. Best validation mAP: {best_map:.4f}")
    return best_path
