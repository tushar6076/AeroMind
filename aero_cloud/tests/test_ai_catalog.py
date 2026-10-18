import json
from io import BytesIO
from pathlib import Path

import torch
from PIL import Image

from app.services.ai.manager import AIService


def _write_router(models_dir: Path, missions: dict[str, str]) -> None:
    (models_dir / "router.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "artifact": "router.pth",
                "runtime": "torchscript",
                "input": {
                    "tensor_shape": [1, 3, 224, 224],
                    "color_order": "RGB",
                    "value_range": [0.0, 1.0],
                },
                "labels": list(missions),
                "missions": missions,
            }
        ),
        encoding="utf-8",
    )
    (models_dir / "router.pth").write_bytes(b"test artifact")


def _write_mission(directory: Path, mission_id: str, artifact: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "metadata.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "id": mission_id,
                "name": mission_id.title(),
                "version": "1",
                "description": f"{mission_id} mission",
                "task": "Classification",
                "router_label": mission_id,
                "input": {
                    "tensor_shape": [1, 3, 224, 224],
                    "color_order": "RGB",
                    "value_range": [0.0, 1.0],
                },
                "stages": [
                    {
                        "id": "classification",
                        "name": "Classification",
                        "artifact": artifact,
                        "task": "Classification",
                        "labels": ["present", "absent"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_inventory_rescans_missions_and_reports_weight_state(tmp_path: Path) -> None:
    _write_router(tmp_path, {"alpha": "alpha"})
    alpha_dir = tmp_path / "alpha"
    _write_mission(alpha_dir, "alpha", "classification.pth")
    service = AIService(tmp_path)

    first_inventory = service.inventory()

    assert first_inventory.router_status == "Weights present; not yet loaded"
    assert [mission.id for mission in first_inventory.models] == ["alpha"]
    assert first_inventory.models[0].status == "Missing stage weights: classification.pth"

    (alpha_dir / "classification.pth").write_bytes(b"test artifact")
    beta_dir = tmp_path / "beta"
    _write_mission(beta_dir, "beta", "classification.pth")
    (beta_dir / "classification.pth").write_bytes(b"test artifact")

    refreshed_inventory = service.inventory()

    assert [mission.id for mission in refreshed_inventory.models] == ["alpha", "beta"]
    assert refreshed_inventory.models[0].status == (
        "Weights present; not yet loaded"
    )
    assert refreshed_inventory.models[1].status == (
        "Router label is not mapped to this mission"
    )


def test_inventory_reports_invalid_mission_metadata(tmp_path: Path) -> None:
    _write_router(tmp_path, {"alpha": "alpha"})
    alpha_dir = tmp_path / "alpha"
    _write_mission(alpha_dir, "different-id", "classification.pth")

    inventory = AIService(tmp_path).inventory()

    assert len(inventory.models) == 1
    assert inventory.models[0].id == "alpha"
    assert inventory.models[0].status == (
        "Invalid metadata: Mission id must match its directory name"
    )


def test_inventory_rejects_artifact_path_outside_mission(tmp_path: Path) -> None:
    _write_router(tmp_path, {"alpha": "alpha"})
    _write_mission(tmp_path / "alpha", "alpha", "../outside.pth")

    inventory = AIService(tmp_path).inventory()

    assert inventory.models[0].status.startswith("Invalid metadata:")
    assert "Artifact path must stay inside its model directory" in (
        inventory.models[0].status
    )


class _ConstantScores(torch.nn.Module):
    def __init__(self, scores: list[float]) -> None:
        super().__init__()
        self.register_buffer("scores", torch.tensor([scores], dtype=torch.float32))

    def forward(self, image: torch.Tensor) -> torch.Tensor:
        return self.scores + image.mean() * 0.0


def _write_torchscript(path: Path, scores: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    model = torch.jit.trace(
        _ConstantScores(scores),
        torch.zeros((1, 3, 224, 224)),
    )
    torch.jit.save(model, str(path))


def _png_bytes() -> bytes:
    image = Image.new("RGB", (12, 10), color=(30, 80, 120))
    stream = BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()


def test_inference_routes_image_and_runs_conditional_mission_stages(
    tmp_path: Path,
) -> None:
    _write_router(tmp_path, {"alpha": "alpha", "other": "other"})
    _write_torchscript(tmp_path / "router.pth", [4.0, 0.0])
    mission_dir = tmp_path / "alpha"
    _write_mission(mission_dir, "alpha", "coarse.pth")
    mission = json.loads((mission_dir / "metadata.json").read_text())
    mission["stages"] = [
        {
            "id": "coarse",
            "name": "Coarse",
            "artifact": "coarse.pth",
            "task": "Coarse classification",
            "labels": ["present", "absent"],
        },
        {
            "id": "detail",
            "name": "Detail",
            "artifact": "detail.pth",
            "task": "Detail classification",
            "labels": ["coat", "shirt"],
            "when": {"coarse": ["present"]},
        },
    ]
    (mission_dir / "metadata.json").write_text(json.dumps(mission), encoding="utf-8")
    _write_torchscript(mission_dir / "coarse.pth", [4.0, 0.0])
    _write_torchscript(mission_dir / "detail.pth", [0.0, 4.0])

    result = AIService(tmp_path).infer(_png_bytes(), "image/png")

    assert result.mission_id == "alpha"
    assert result.router_label == "alpha"
    assert [stage.status for stage in result.stages] == ["predicted", "predicted"]
    assert [stage.label for stage in result.stages] == ["present", "shirt"]
    assert all(stage.confidence is not None for stage in result.stages)


def test_inference_skips_unmatched_stage_without_loading_its_weights(
    tmp_path: Path,
) -> None:
    _write_router(tmp_path, {"alpha": "alpha", "other": "other"})
    _write_torchscript(tmp_path / "router.pth", [4.0, 0.0])
    mission_dir = tmp_path / "alpha"
    _write_mission(mission_dir, "alpha", "coarse.pth")
    mission = json.loads((mission_dir / "metadata.json").read_text())
    mission["stages"] = [
        {
            "id": "coarse",
            "name": "Coarse",
            "artifact": "coarse.pth",
            "task": "Coarse classification",
            "labels": ["present", "absent"],
        },
        {
            "id": "detail",
            "name": "Detail",
            "artifact": "missing_detail.pth",
            "task": "Detail classification",
            "labels": ["coat", "shirt"],
            "when": {"coarse": ["present"]},
        },
    ]
    (mission_dir / "metadata.json").write_text(json.dumps(mission), encoding="utf-8")
    _write_torchscript(mission_dir / "coarse.pth", [0.0, 4.0])

    result = AIService(tmp_path).infer(_png_bytes(), "image/png")

    assert result.stages[0].label == "absent"
    assert result.stages[1].status == "skipped"
    assert result.stages[1].label is None
    assert result.stages[1].confidence is None
