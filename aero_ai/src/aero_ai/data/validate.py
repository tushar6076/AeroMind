from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image

from aero_ai.data.coco import CocoDetectionDataset


def validate_coco_dataset(
    image_dir: str | Path,
    annotation_file: str | Path,
    class_names: tuple[str, ...],
) -> dict[str, Any]:
    dataset = CocoDetectionDataset(image_dir, annotation_file, class_names)
    counts: Counter[str] = Counter()
    empty_images = 0
    for image_id, image_info in dataset.images.items():
        image_path = (dataset.image_dir / str(image_info["file_name"])).resolve()
        if not image_path.is_relative_to(dataset.image_dir):
            raise ValueError(f"Image path escapes its dataset root: {image_info['file_name']}")
        if not image_path.is_file():
            raise FileNotFoundError(f"Referenced image does not exist: {image_path}")
        with Image.open(image_path) as image:
            width, height = image.size
        expected = (int(image_info.get("width", width)), int(image_info.get("height", height)))
        if (width, height) != expected:
            raise ValueError(
                f"Image dimensions differ from COCO metadata for {image_path}: "
                f"metadata={expected[0]}x{expected[1]}, actual={width}x{height}"
            )
        annotations = dataset.annotations_by_image[image_id]
        if not annotations:
            empty_images += 1
        for item in annotations:
            counts[class_names[item["label"] - 1]] += 1
    return {
        "images": len(dataset),
        "annotations": sum(counts.values()),
        "empty_images": empty_images,
        "classes": {name: counts[name] for name in class_names},
        "image_dir": str(dataset.image_dir),
        "annotation_file": str(dataset.annotation_file),
    }
