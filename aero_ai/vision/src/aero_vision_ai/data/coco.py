from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision.transforms import functional as TF

from aero_vision_ai.data.transforms import DetectionHorizontalFlip


class CocoDetectionDataset(Dataset):
    """COCO aerial object-detection dataset with continuous 1..N remapping."""

    def __init__(
        self,
        image_dir: str | Path,
        annotation_file: str | Path,
        class_names: tuple[str, ...],
        *,
        augment: bool = False,
        horizontal_flip_probability: float = 0.5,
    ) -> None:
        self.image_dir = Path(image_dir).resolve()
        self.annotation_file = Path(annotation_file).resolve()
        self.class_names = tuple(class_names)
        self.augment = augment
        self.transform = (
            DetectionHorizontalFlip(probability=horizontal_flip_probability)
            if augment
            else None
        )

        with self.annotation_file.open("r", encoding="utf-8") as stream:
            document = json.load(stream)
        if not isinstance(document, dict):
            raise ValueError(f"COCO file must contain a JSON object: {self.annotation_file}")

        self.images = self._index_images(document.get("images"))
        self.category_map = self._index_categories(document.get("categories"))
        self.annotations_by_image = self._index_annotations(document.get("annotations"))

    def _index_images(self, images: Any) -> dict[int, dict[str, Any]]:
        if not isinstance(images, list) or not images:
            raise ValueError(f"COCO file has no images: {self.annotation_file}")
        indexed: dict[int, dict[str, Any]] = {}
        for item in images:
            if not isinstance(item, dict) or not {"id", "file_name"}.issubset(item):
                raise ValueError("Every COCO image requires 'id' and 'file_name'.")
            image_id = int(item["id"])
            if image_id in indexed:
                raise ValueError(f"Duplicate COCO image id: {image_id}")
            file_name = Path(str(item["file_name"]))
            if file_name.is_absolute() or ".." in file_name.parts:
                raise ValueError(f"Image path escapes dataset root: {file_name}")
            indexed[image_id] = item
        return indexed

    def _index_categories(self, categories: Any) -> dict[int, int]:
        if not isinstance(categories, list) or not categories:
            raise ValueError(f"COCO file has no categories: {self.annotation_file}")
        expected = {name: index + 1 for index, name in enumerate(self.class_names)}
        mapping: dict[int, int] = {}
        found_names: set[str] = set()
        for category in categories:
            if not isinstance(category, dict) or not {"id", "name"}.issubset(category):
                raise ValueError("Every COCO category requires 'id' and 'name'.")
            name = str(category["name"])
            category_id = int(category["id"])
            if name not in expected:
                raise ValueError(
                    f"Unexpected category '{name}'. Configured categories: {list(self.class_names)}"
                )
            if category_id in mapping or name in found_names:
                raise ValueError(f"Duplicate COCO category id or name: {category}")
            found_names.add(name)
            mapping[category_id] = expected[name]
        if found_names != set(self.class_names):
            missing = sorted(set(self.class_names) - found_names)
            raise ValueError(f"COCO categories missing configured classes: {missing}")
        return mapping

    def _index_annotations(self, annotations: Any) -> dict[int, list[dict[str, Any]]]:
        if not isinstance(annotations, list):
            raise ValueError("COCO annotation file requires an 'annotations' list.")
        indexed = {image_id: [] for image_id in self.images}
        for annotation in annotations:
            if not isinstance(annotation, dict):
                raise ValueError("Each COCO annotation must be a JSON object.")
            required = {"image_id", "category_id", "bbox"}
            if not required.issubset(annotation):
                raise ValueError(f"COCO annotation missing fields: {sorted(required - annotation.keys())}")
            image_id = int(annotation["image_id"])
            category_id = int(annotation["category_id"])
            if image_id not in indexed:
                raise ValueError(f"Annotation references unknown image id: {image_id}")
            if category_id not in self.category_map:
                raise ValueError(f"Annotation references unknown category id: {category_id}")
            if int(annotation.get("iscrowd", 0)) == 1:
                continue

            bbox = annotation["bbox"]
            if not isinstance(bbox, list) or len(bbox) != 4:
                raise ValueError("COCO bbox must be [x, y, width, height].")
            x, y, width, height = (float(v) for v in bbox)
            if not all(math.isfinite(v) for v in (x, y, width, height)):
                raise ValueError(f"COCO bbox contains non-finite values: {bbox}")
            if x < 0 or y < 0 or width <= 0 or height <= 0:
                raise ValueError(f"COCO bbox must have non-negative origin and positive size: {bbox}")

            image_info = self.images[image_id]
            image_width = int(image_info.get("width", 0))
            image_height = int(image_info.get("height", 0))
            if image_width and x + width > image_width + 1:
                raise ValueError(f"COCO bbox exceeds image width for image id {image_id}: {bbox}")
            if image_height and y + height > image_height + 1:
                raise ValueError(f"COCO bbox exceeds image height for image id {image_id}: {bbox}")

            indexed[image_id].append(
                {"bbox": (x, y, x + width, y + height), "label": self.category_map[category_id]}
            )
        return indexed

    def __len__(self) -> int:
        return len(self.images)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
        image_id = sorted(self.images)[index]
        image_info = self.images[image_id]
        image_path = (self.image_dir / str(image_info["file_name"])).resolve()
        if not image_path.is_relative_to(self.image_dir):
            raise ValueError(f"Image path escapes root: {image_info['file_name']}")

        with Image.open(image_path) as image_file:
            image = image_file.convert("RGB")
            actual_width, actual_height = image.size
            image_tensor = TF.pil_to_tensor(image).to(torch.float32) / 255.0

        objects = self.annotations_by_image[image_id]
        boxes = torch.tensor([item["bbox"] for item in objects], dtype=torch.float32).reshape(-1, 4)
        labels = torch.tensor([item["label"] for item in objects], dtype=torch.int64)

        target = {
            "boxes": boxes,
            "labels": labels,
            "image_id": torch.tensor(image_id, dtype=torch.int64),
            "area": (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1]) if len(boxes) else torch.empty((0,)),
            "iscrowd": torch.zeros((len(boxes),), dtype=torch.int64),
        }

        if self.transform:
            image_tensor, target = self.transform(image_tensor, target, actual_width)

        return image_tensor, target


def collate_detections(
    batch: list[tuple[torch.Tensor, dict[str, torch.Tensor]]],
) -> tuple[list[torch.Tensor], list[dict[str, torch.Tensor]]]:
    images, targets = zip(*batch)
    return list(images), list(targets)