from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


@dataclass(frozen=True)
class StageConfig:
    id: str
    name: str
    task: str
    labels: tuple[str, ...]
    train_dir: Path
    val_dir: Path
    when: dict[str, list[str]] | None


@dataclass(frozen=True)
class MissionConfig:
    id: str
    name: str
    version: str
    description: str
    task: str
    router_label: str
    stages: tuple[StageConfig, ...]


@dataclass(frozen=True)
class MissionsConfig:
    root: Path
    registry_dir: Path
    input_size: int
    epochs: int
    batch_size: int
    num_workers: int
    learning_rate: float
    seed: int
    router_train_dir: Path
    router_val_dir: Path
    missions: tuple[MissionConfig, ...]


class ImageClassifier(nn.Module):
    def __init__(self, class_count: int) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Linear(64, class_count)

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        features = self.features(images)
        return self.classifier(torch.flatten(features, 1))


def _mapping(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{location} must be a YAML mapping")
    return value


def _resolve(root: Path, value: Any, location: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} must be a non-empty path")
    path = Path(value).expanduser()
    return (root / path).resolve() if not path.is_absolute() else path.resolve()


def _labels(value: Any, location: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or any(
        not isinstance(label, str) or not label.strip() for label in value
    ):
        raise ValueError(f"{location} must be a non-empty list of labels")
    labels = tuple(value)
    if len(labels) < 2:
        raise ValueError(f"{location} must contain at least two class labels")
    if len(set(labels)) != len(labels):
        raise ValueError(f"{location} must not contain duplicate labels")
    return labels


def load_missions_config(config_path: str | Path) -> MissionsConfig:
    config_file = Path(config_path).expanduser().resolve()
    with config_file.open("r", encoding="utf-8") as stream:
        raw = _mapping(yaml.safe_load(stream), "configuration")
    root = config_file.parent.parent

    training = _mapping(raw.get("training"), "training")
    router = _mapping(raw.get("router"), "router")
    raw_missions = _mapping(raw.get("missions"), "missions")
    if len(raw_missions) < 2:
        raise ValueError("missions must define at least two router categories")

    missions = []
    for mission_id, raw_mission in raw_missions.items():
        if not isinstance(mission_id, str) or not re.fullmatch(
            r"[a-z0-9][a-z0-9_-]*", mission_id
        ):
            raise ValueError(
                "Mission ids must be lowercase identifiers using letters, digits, "
                "underscores, or hyphens"
            )
        mission = _mapping(raw_mission, f"missions.{mission_id}")
        raw_stages = mission.get("stages")
        if not isinstance(raw_stages, list) or not raw_stages:
            raise ValueError(f"missions.{mission_id}.stages must be a non-empty list")
        stages = []
        seen_stage_ids: set[str] = set()
        prior_labels: dict[str, set[str]] = {}
        for index, raw_stage in enumerate(raw_stages):
            location = f"missions.{mission_id}.stages[{index}]"
            stage = _mapping(raw_stage, location)
            stage_id = stage.get("id")
            if not isinstance(stage_id, str) or not re.fullmatch(
                r"[a-z0-9][a-z0-9_-]*", stage_id
            ) or stage_id in seen_stage_ids:
                raise ValueError(
                    f"{location}.id must be a unique lowercase identifier"
                )
            labels = _labels(stage.get("labels"), f"{location}.labels")
            when = stage.get("when")
            if when is not None:
                when = _mapping(when, f"{location}.when")
                if len(when) != 1:
                    raise ValueError(f"{location}.when must name one preceding stage")
                prior_id, prior_values = next(iter(when.items()))
                if prior_id not in prior_labels:
                    raise ValueError(f"{location}.when must reference a preceding stage")
                if (
                    not isinstance(prior_values, list)
                    or any(not isinstance(label, str) for label in prior_values)
                    or not set(prior_values).issubset(prior_labels[prior_id])
                ):
                    raise ValueError(f"{location}.when contains unknown stage labels")
                when = {prior_id: list(prior_values)}
            stages.append(
                StageConfig(
                    id=stage_id,
                    name=str(stage.get("name", stage_id)),
                    task=str(stage.get("task", stage_id)),
                    labels=labels,
                    train_dir=_resolve(root, stage.get("train_dir"), f"{location}.train_dir"),
                    val_dir=_resolve(root, stage.get("val_dir"), f"{location}.val_dir"),
                    when=when,
                )
            )
            seen_stage_ids.add(stage_id)
            prior_labels[stage_id] = set(labels)
        router_label = mission.get("router_label", mission_id)
        if not isinstance(router_label, str) or not router_label:
            raise ValueError(f"missions.{mission_id}.router_label must be non-empty")
        missions.append(
            MissionConfig(
                id=mission_id,
                name=str(mission.get("name", mission_id)),
                version=str(mission.get("version", "1")),
                description=str(mission.get("description", "")),
                task=str(mission.get("task", mission_id)),
                router_label=router_label,
                stages=tuple(stages),
            )
        )
    router_labels = [mission.router_label for mission in missions]
    if len(set(router_labels)) != len(router_labels):
        raise ValueError("Mission router_label values must be unique")

    input_size = int(raw.get("input_size", 224))
    epochs = int(training.get("epochs", 10))
    batch_size = int(training.get("batch_size", 16))
    num_workers = int(training.get("num_workers", 0))
    learning_rate = float(training.get("learning_rate", 0.001))
    if input_size < 16 or epochs <= 0 or batch_size <= 0 or num_workers < 0:
        raise ValueError(
            "input_size must be at least 16; epochs and batch_size must be positive; "
            "num_workers non-negative"
        )
    if learning_rate <= 0:
        raise ValueError("training.learning_rate must be positive")

    router_dir = _resolve(root, router.get("dataset_dir"), "router.dataset_dir")
    return MissionsConfig(
        root=root,
        registry_dir=_resolve(root, raw.get("registry_dir"), "registry_dir"),
        input_size=input_size,
        epochs=epochs,
        batch_size=batch_size,
        num_workers=num_workers,
        learning_rate=learning_rate,
        seed=int(training.get("seed", 42)),
        router_train_dir=router_dir / "train",
        router_val_dir=router_dir / "val",
        missions=tuple(missions),
    )


def _image_dataset(
    directory: Path,
    labels: tuple[str, ...],
    image_size: int,
) -> datasets.ImageFolder:
    if not directory.is_dir():
        raise FileNotFoundError(f"Image dataset directory does not exist: {directory}")
    dataset = datasets.ImageFolder(
        str(directory),
        transform=transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
            ]
        ),
    )
    if set(dataset.classes) != set(labels):
        raise ValueError(
            f"Dataset classes in {directory} must exactly match {list(labels)}; "
            f"found {dataset.classes}"
        )
    class_indices = {label: index for index, label in enumerate(labels)}
    dataset.samples = [
        (path, class_indices[dataset.classes[class_index]])
        for path, class_index in dataset.samples
    ]
    dataset.imgs = dataset.samples
    dataset.targets = [target for _, target in dataset.samples]
    if not dataset.samples:
        raise ValueError(f"No labeled images found in {directory}")
    return dataset


def _loaders(
    train_dir: Path,
    val_dir: Path,
    labels: tuple[str, ...],
    config: MissionsConfig,
) -> tuple[DataLoader, DataLoader]:
    train_dataset = _image_dataset(train_dir, labels, config.input_size)
    val_dataset = _image_dataset(val_dir, labels, config.input_size)
    options = {
        "batch_size": config.batch_size,
        "num_workers": config.num_workers,
    }
    return (
        DataLoader(train_dataset, shuffle=True, **options),
        DataLoader(val_dataset, shuffle=False, **options),
    )


def _train_classifier(
    train_dir: Path,
    val_dir: Path,
    labels: tuple[str, ...],
    config: MissionsConfig,
    artifact: Path,
    device: torch.device,
) -> float:
    train_loader, val_loader = _loaders(train_dir, val_dir, labels, config)
    model = ImageClassifier(len(labels)).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    loss_function = nn.CrossEntropyLoss()
    best_accuracy = -1.0
    best_state: dict[str, torch.Tensor] | None = None

    for epoch in range(config.epochs):
        model.train()
        for images, targets in train_loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model(images), targets)
            if not torch.isfinite(loss):
                raise FloatingPointError(f"Non-finite classification loss for {artifact}")
            loss.backward()
            optimizer.step()

        model.eval()
        correct = total = 0
        with torch.inference_mode():
            for images, targets in val_loader:
                predictions = model(images.to(device)).argmax(dim=1).cpu()
                correct += int((predictions == targets).sum())
                total += int(targets.numel())
        accuracy = correct / total
        print(
            f"{artifact.parent.name}/{artifact.stem} "
            f"epoch {epoch + 1}/{config.epochs}: val_accuracy={accuracy:.4f}"
        )
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }

    if best_state is None:
        raise RuntimeError(f"Training produced no checkpoint for {artifact}")
    model.load_state_dict(best_state)
    model.eval()
    artifact.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = artifact.with_name(f".{artifact.name}.tmp")
    torch.jit.save(torch.jit.script(model.cpu()), str(temporary_path))
    temporary_path.replace(artifact)
    return best_accuracy


def _metadata_input(image_size: int) -> dict[str, Any]:
    return {
        "tensor_shape": [1, 3, image_size, image_size],
        "color_order": "RGB",
        "value_range": [0.0, 1.0],
    }


def train_missions(
    config: MissionsConfig,
    device: torch.device | None = None,
) -> dict[str, float]:
    random.seed(config.seed)
    np.random.seed(config.seed)
    torch.manual_seed(config.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(config.seed)
    selected_device = device or torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )
    router_labels = tuple(mission.router_label for mission in config.missions)
    _loaders(
        config.router_train_dir,
        config.router_val_dir,
        router_labels,
        config,
    )
    for mission in config.missions:
        for stage in mission.stages:
            _loaders(stage.train_dir, stage.val_dir, stage.labels, config)

    config.registry_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, float] = {}

    results["router"] = _train_classifier(
        config.router_train_dir,
        config.router_val_dir,
        router_labels,
        config,
        config.registry_dir / "router.pth",
        selected_device,
    )

    router_metadata = {
        "schema_version": 1,
        "artifact": "router.pth",
        "runtime": "torchscript",
        "input": _metadata_input(config.input_size),
        "labels": list(router_labels),
        "missions": {
            mission.router_label: mission.id for mission in config.missions
        },
    }

    for mission in config.missions:
        mission_dir = config.registry_dir / mission.id
        metadata_stages = []
        for stage in mission.stages:
            artifact_name = f"{stage.id}.pth"
            results[f"{mission.id}/{stage.id}"] = _train_classifier(
                stage.train_dir,
                stage.val_dir,
                stage.labels,
                config,
                mission_dir / artifact_name,
                selected_device,
            )
            stage_metadata: dict[str, Any] = {
                "id": stage.id,
                "name": stage.name,
                "artifact": artifact_name,
                "task": stage.task,
                "labels": list(stage.labels),
            }
            if stage.when is not None:
                stage_metadata["when"] = stage.when
            metadata_stages.append(stage_metadata)
        mission_metadata = {
            "schema_version": 1,
            "id": mission.id,
            "name": mission.name,
            "version": mission.version,
            "description": mission.description,
            "task": mission.task,
            "router_label": mission.router_label,
            "input": _metadata_input(config.input_size),
            "stages": metadata_stages,
        }
        _write_json(mission_dir / "metadata.json", mission_metadata)

    _write_json(config.registry_dir / "router.json", router_metadata)
    return results


def _write_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f".{path.name}.tmp")
    temporary_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    temporary_path.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="vision-missions",
        description="Train the router and every configured hierarchical mission stage.",
    )
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[2] / "configs" / "missions.yaml"),
        help="Mission training YAML configuration.",
    )
    args = parser.parse_args()
    config = load_missions_config(args.config)
    results = train_missions(config)
    print(f"Mission training complete. TorchScript registry: {config.registry_dir}")
    for model_id, accuracy in results.items():
        print(f"  {model_id}: validation accuracy {accuracy:.4f}")


if __name__ == "__main__":
    main()
