import json

import pytest
import torch
import yaml
from PIL import Image

from aero_vision_ai.mission_training import load_missions_config, train_missions


def _write_images(directory, labels):
    for label_index, label in enumerate(labels):
        class_dir = directory / label
        class_dir.mkdir(parents=True)
        for image_index in range(2):
            Image.new(
                "RGB",
                (32, 32),
                color=(label_index * 80, image_index * 80, 40),
            ).save(class_dir / f"{image_index}.png")


def _configuration(tmp_path):
    labels_by_dataset = {
        "router/train": ["alpha", "beta"],
        "router/val": ["alpha", "beta"],
        "alpha/coarse/train": ["adult", "child"],
        "alpha/coarse/val": ["adult", "child"],
        "alpha/detail/train": ["coat", "shirt"],
        "alpha/detail/val": ["coat", "shirt"],
        "beta/type/train": ["car", "truck"],
        "beta/type/val": ["car", "truck"],
    }
    for relative, labels in labels_by_dataset.items():
        _write_images(tmp_path / "data" / relative, labels)
    config = {
        "registry_dir": "registry",
        "input_size": 32,
        "training": {
            "epochs": 1,
            "batch_size": 2,
            "num_workers": 0,
            "learning_rate": 0.001,
            "seed": 11,
        },
        "router": {"dataset_dir": "data/router"},
        "missions": {
            "alpha": {
                "name": "Alpha",
                "router_label": "alpha",
                "stages": [
                    {
                        "id": "coarse",
                        "name": "Coarse",
                        "task": "Coarse classification",
                        "labels": ["adult", "child"],
                        "train_dir": "data/alpha/coarse/train",
                        "val_dir": "data/alpha/coarse/val",
                    },
                    {
                        "id": "detail",
                        "name": "Detail",
                        "task": "Detail classification",
                        "labels": ["coat", "shirt"],
                        "train_dir": "data/alpha/detail/train",
                        "val_dir": "data/alpha/detail/val",
                        "when": {"coarse": ["adult"]},
                    },
                ],
            },
            "beta": {
                "name": "Beta",
                "router_label": "beta",
                "stages": [
                    {
                        "id": "type",
                        "name": "Type",
                        "task": "Type classification",
                        "labels": ["car", "truck"],
                        "train_dir": "data/beta/type/train",
                        "val_dir": "data/beta/type/val",
                    }
                ],
            },
        },
    }
    config_path = tmp_path / "configs" / "missions.yaml"
    config_path.parent.mkdir()
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return config_path


def test_mission_training_exports_router_and_all_stages(tmp_path):
    config = load_missions_config(_configuration(tmp_path))

    results = train_missions(config, device=torch.device("cpu"))

    assert set(results) == {"router", "alpha/coarse", "alpha/detail", "beta/type"}
    registry = tmp_path / "registry"
    assert (registry / "router.pth").is_file()
    router_metadata = json.loads((registry / "router.json").read_text())
    assert router_metadata["missions"] == {"alpha": "alpha", "beta": "beta"}
    alpha_metadata = json.loads((registry / "alpha" / "metadata.json").read_text())
    assert [stage["id"] for stage in alpha_metadata["stages"]] == ["coarse", "detail"]
    assert alpha_metadata["stages"][1]["when"] == {"coarse": ["adult"]}
    for artifact in (
        registry / "alpha" / "coarse.pth",
        registry / "alpha" / "detail.pth",
        registry / "beta" / "type.pth",
    ):
        assert artifact.is_file()
        model = torch.jit.load(str(artifact))
        assert model(torch.zeros((1, 3, 32, 32))).shape == (1, 2)


def test_mission_training_rejects_unknown_condition_label(tmp_path):
    config_path = _configuration(tmp_path)
    raw = yaml.safe_load(config_path.read_text())
    raw["missions"]["alpha"]["stages"][1]["when"] = {"coarse": ["missing"]}
    config_path.write_text(yaml.safe_dump(raw), encoding="utf-8")

    with pytest.raises(ValueError, match="unknown stage labels"):
        load_missions_config(config_path)
