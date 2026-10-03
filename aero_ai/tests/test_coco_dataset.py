import json
from pathlib import Path

import pytest
import torch
from PIL import Image

from aero_ai.data import CocoDetectionDataset, validate_coco_dataset


def write_dataset(root: Path, file_name: str = "frame.png") -> tuple[Path, Path]:
    image_dir = root / "images"
    image_dir.mkdir(parents=True)
    Image.new("RGB", (20, 10), color="white").save(image_dir / file_name)
    annotations_path = root / "annotations.json"
    annotations_path.write_text(
        json.dumps(
            {
                "images": [{"id": 1, "file_name": file_name, "width": 20, "height": 10}],
                "categories": [
                    {"id": 4, "name": "person"},
                    {"id": 9, "name": "vehicle"},
                ],
                "annotations": [
                    {"id": 1, "image_id": 1, "category_id": 4, "bbox": [2, 1, 5, 4]},
                    {"id": 2, "image_id": 1, "category_id": 9, "bbox": [10, 2, 4, 5]},
                ],
            }
        ),
        encoding="utf-8",
    )
    return image_dir, annotations_path


def test_coco_dataset_maps_labels_and_xywh_to_xyxy(tmp_path: Path) -> None:
    image_dir, annotation_path = write_dataset(tmp_path)
    dataset = CocoDetectionDataset(image_dir, annotation_path, ("person", "vehicle"))

    image, target = dataset[0]

    assert image.shape == (3, 10, 20)
    assert torch.allclose(target["boxes"], torch.tensor([[2, 1, 7, 5], [10, 2, 14, 7.0]]))
    assert target["labels"].tolist() == [1, 2]


def test_horizontal_flip_updates_boxes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    image_dir, annotation_path = write_dataset(tmp_path)
    monkeypatch.setattr("aero_ai.data.coco.random.random", lambda: 0.0)
    dataset = CocoDetectionDataset(
        image_dir,
        annotation_path,
        ("person", "vehicle"),
        augment=True,
        horizontal_flip_probability=1.0,
    )

    _, target = dataset[0]

    assert torch.allclose(target["boxes"], torch.tensor([[13, 1, 18, 5], [6, 2, 10, 7.0]]))


def test_validator_reports_empty_images_and_class_counts(tmp_path: Path) -> None:
    image_dir, annotation_path = write_dataset(tmp_path)

    result = validate_coco_dataset(image_dir, annotation_path, ("person", "vehicle"))

    assert result["images"] == 1
    assert result["annotations"] == 2
    assert result["classes"] == {"person": 1, "vehicle": 1}
    assert result["empty_images"] == 0


def test_empty_image_has_empty_boxes_and_is_reported(tmp_path: Path) -> None:
    image_dir, annotation_path = write_dataset(tmp_path)
    document = json.loads(annotation_path.read_text(encoding="utf-8"))
    document["annotations"] = []
    annotation_path.write_text(json.dumps(document), encoding="utf-8")
    dataset = CocoDetectionDataset(image_dir, annotation_path, ("person", "vehicle"))

    _, target = dataset[0]
    report = validate_coco_dataset(image_dir, annotation_path, ("person", "vehicle"))

    assert target["boxes"].shape == (0, 4)
    assert target["labels"].shape == (0,)
    assert report["empty_images"] == 1
    assert report["annotations"] == 0


def test_dataset_rejects_paths_outside_image_root(tmp_path: Path) -> None:
    image_dir, annotation_path = write_dataset(tmp_path)
    document = json.loads(annotation_path.read_text(encoding="utf-8"))
    document["images"][0]["file_name"] = "../outside.png"
    annotation_path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match="relative"):
        CocoDetectionDataset(image_dir, annotation_path, ("person", "vehicle"))
