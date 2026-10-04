from __future__ import annotations

from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm


def _box_iou(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    left_top = np.maximum(box[:2], boxes[:, :2])
    right_bottom = np.minimum(box[2:], boxes[:, 2:])
    intersection_size = np.maximum(right_bottom - left_top, 0)
    intersection = intersection_size[:, 0] * intersection_size[:, 1]
    box_area = np.maximum(box[2] - box[0], 0) * np.maximum(box[3] - box[1], 0)
    boxes_area = (
        np.maximum(boxes[:, 2] - boxes[:, 0], 0)
        * np.maximum(boxes[:, 3] - boxes[:, 1], 0)
    )
    return intersection / np.maximum(box_area + boxes_area - intersection, 1e-12)


def _average_precision(
    predictions: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    class_id: int,
    iou_threshold: float,
) -> tuple[float, int, int]:
    ground_truth_by_image: dict[int, np.ndarray] = {}
    for target in targets:
        mask = target["labels"] == class_id
        ground_truth_by_image[int(target["image_id"])] = target["boxes"][mask]
    ground_truth_count = sum(len(boxes) for boxes in ground_truth_by_image.values())
    if ground_truth_count == 0:
        return 0.0, 0, 0

    matched = {
        image_id: np.zeros(len(boxes), dtype=bool)
        for image_id, boxes in ground_truth_by_image.items()
    }
    candidates: list[tuple[float, int, np.ndarray]] = []
    for prediction in predictions:
        mask = (prediction["labels"] == class_id) & (prediction["scores"] > 0)
        for box, score in zip(prediction["boxes"][mask], prediction["scores"][mask]):
            candidates.append((float(score), int(prediction["image_id"]), box))
    candidates.sort(key=lambda item: item[0], reverse=True)

    true_positives = np.zeros(len(candidates), dtype=np.float64)
    false_positives = np.zeros(len(candidates), dtype=np.float64)
    for index, (_, image_id, predicted_box) in enumerate(candidates):
        image_boxes = ground_truth_by_image.get(image_id, np.empty((0, 4)))
        if not len(image_boxes):
            false_positives[index] = 1
            continue
        overlaps = _box_iou(predicted_box, image_boxes)
        best_index = int(np.argmax(overlaps))
        if overlaps[best_index] >= iou_threshold and not matched[image_id][best_index]:
            true_positives[index] = 1
            matched[image_id][best_index] = True
        else:
            false_positives[index] = 1

    if not len(candidates):
        return 0.0, ground_truth_count, 0
    cumulative_tp = np.cumsum(true_positives)
    cumulative_fp = np.cumsum(false_positives)
    recall = cumulative_tp / ground_truth_count
    precision = cumulative_tp / np.maximum(cumulative_tp + cumulative_fp, 1e-12)
    recall_points = np.linspace(0, 1, 101)
    interpolated_precision = [
        np.max(precision[recall >= point], initial=0.0) for point in recall_points
    ]
    return float(np.mean(interpolated_precision)), ground_truth_count, len(candidates)


def evaluate_predictions(
    predictions: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    class_names: tuple[str, ...],
    iou_thresholds: tuple[float, ...] = (0.5, 0.75),
    score_threshold: float = 0.25,
) -> dict[str, Any]:
    if len(predictions) != len(targets):
        raise ValueError("Prediction and target lists must have the same number of images.")

    normalized_predictions: list[dict[str, Any]] = []
    normalized_targets: list[dict[str, Any]] = []
    for prediction, target in zip(predictions, targets):
        normalized_predictions.append(
            {
                "image_id": int(target["image_id"]),
                "boxes": np.asarray(prediction["boxes"], dtype=np.float64).reshape(-1, 4),
                "labels": np.asarray(prediction["labels"], dtype=np.int64).reshape(-1),
                "scores": np.asarray(prediction["scores"], dtype=np.float64).reshape(-1),
            }
        )
        normalized_targets.append(
            {
                "image_id": int(target["image_id"]),
                "boxes": np.asarray(target["boxes"], dtype=np.float64).reshape(-1, 4),
                "labels": np.asarray(target["labels"], dtype=np.int64).reshape(-1),
            }
        )

    class_metrics: dict[str, Any] = {}
    all_class_aps: list[list[float]] = [[] for _ in iou_thresholds]
    total_ground_truths = 0

    for class_id, class_name in enumerate(class_names, start=1):
        ap_values: list[float] = []
        ground_truth_count = 0
        for threshold_index, iou_threshold in enumerate(iou_thresholds):
            ap, count, _ = _average_precision(
                normalized_predictions, normalized_targets, class_id, iou_threshold
            )
            ap_values.append(ap)
            ground_truth_count = count
            if count > 0:
                all_class_aps[threshold_index].append(ap)

        ap50 = ap_values[iou_thresholds.index(0.5)] if 0.5 in iou_thresholds else None
        ap75 = ap_values[iou_thresholds.index(0.75)] if 0.75 in iou_thresholds else None

        class_metrics[class_name] = {
            "ground_truths": ground_truth_count,
            "ap_by_iou": {str(t): float(a) for t, a in zip(iou_thresholds, ap_values)},
            "ap50": float(ap50) if ap50 is not None else None,
            "ap75": float(ap75) if ap75 is not None else None,
            "mean_ap": float(np.mean(ap_values)) if ap_values else 0.0,
        }
        total_ground_truths += ground_truth_count

    mean_ap_per_threshold = [float(np.mean(v)) if v else 0.0 for v in all_class_aps]

    # Only aggregate classes that actually have ground truth instances and valid metrics
    valid_ap50 = [
        float(m["ap50"])
        for m in class_metrics.values()
        if m["ground_truths"] > 0 and m["ap50"] is not None
    ]
    valid_ap75 = [
        float(m["ap75"])
        for m in class_metrics.values()
        if m["ground_truths"] > 0 and m["ap75"] is not None
    ]

    return {
        "map": float(np.mean(mean_ap_per_threshold)) if mean_ap_per_threshold else 0.0,
        "map_by_iou": {str(t): float(v) for t, v in zip(iou_thresholds, mean_ap_per_threshold)},
        "map50": float(np.mean(valid_ap50)) if valid_ap50 else None,
        "map75": float(np.mean(valid_ap75)) if valid_ap75 else None,
        "classes": class_metrics,
    }


@torch.inference_mode()
def evaluate_model(
    model: torch.nn.Module,
    loader: DataLoader,
    device: torch.device,
    class_names: tuple[str, ...],
    iou_thresholds: tuple[float, ...],
    score_threshold: float,
) -> dict[str, Any]:
    model.eval()
    predictions: list[dict[str, Any]] = []
    targets: list[dict[str, Any]] = []
    for images, batch_targets in tqdm(loader, desc="Evaluating", leave=False):
        outputs = model([img.to(device) for img in images])
        for output, target in zip(outputs, batch_targets):
            predictions.append(
                {
                    "boxes": output["boxes"].detach().cpu(),
                    "labels": output["labels"].detach().cpu(),
                    "scores": output["scores"].detach().cpu(),
                }
            )
            targets.append(
                {
                    "image_id": int(target["image_id"]),
                    "boxes": target["boxes"].cpu(),
                    "labels": target["labels"].cpu(),
                }
            )
    return evaluate_predictions(
        predictions, targets, class_names, iou_thresholds, score_threshold
    )