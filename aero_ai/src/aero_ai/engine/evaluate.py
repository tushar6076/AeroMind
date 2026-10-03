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
    if not 0 <= score_threshold <= 1:
        raise ValueError("score_threshold must be between 0 and 1.")
    if not iou_thresholds or any(not 0 < threshold <= 1 for threshold in iou_thresholds):
        raise ValueError("iou_thresholds must contain values in (0, 1].")

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
    total_true_positives = 0
    total_false_positives = 0
    total_ground_truths = 0
    threshold_for_counts = iou_thresholds[0]

    for class_id, class_name in enumerate(class_names, start=1):
        ap_values: list[float] = []
        ground_truth_count = 0
        for threshold_index, iou_threshold in enumerate(iou_thresholds):
            ap, count, _ = _average_precision(
                normalized_predictions, normalized_targets, class_id, iou_threshold
            )
            ap_values.append(ap)
            ground_truth_count = count
            if count:
                all_class_aps[threshold_index].append(ap)

        ap50 = ap_values[iou_thresholds.index(0.5)] if 0.5 in iou_thresholds else None
        ap75 = ap_values[iou_thresholds.index(0.75)] if 0.75 in iou_thresholds else None
        class_metrics[class_name] = {
            "ground_truths": ground_truth_count,
            "ap_by_iou": {
                str(threshold): ap
                for threshold, ap in zip(iou_thresholds, ap_values)
            },
            "ap50": ap50,
            "ap75": ap75,
            "mean_ap": float(np.mean(ap_values)) if ap_values else 0.0,
        }
        total_ground_truths += ground_truth_count

        if threshold_for_counts in iou_thresholds:
            _, count, _ = _average_precision(
                normalized_predictions,
                normalized_targets,
                class_id,
                threshold_for_counts,
            )
            selected = [
                (
                    float(score),
                    int(prediction["image_id"]),
                    box,
                )
                for prediction in normalized_predictions
                for box, label, score in zip(
                    prediction["boxes"], prediction["labels"], prediction["scores"]
                )
                if int(label) == class_id and float(score) >= score_threshold
            ]
            selected.sort(key=lambda item: item[0], reverse=True)
            matched_by_image = {
                int(target["image_id"]): np.zeros(
                    int(np.sum(target["labels"] == class_id)), dtype=bool
                )
                for target in normalized_targets
            }
            ground_truth_by_image = {
                int(target["image_id"]): target["boxes"][target["labels"] == class_id]
                for target in normalized_targets
            }
            class_tp = 0
            class_fp = 0
            for _, image_id, box in selected:
                image_boxes = ground_truth_by_image.get(image_id, np.empty((0, 4)))
                if not len(image_boxes):
                    class_fp += 1
                    continue
                overlaps = _box_iou(box, image_boxes)
                best_index = int(np.argmax(overlaps))
                if (
                    overlaps[best_index] >= threshold_for_counts
                    and not matched_by_image[image_id][best_index]
                ):
                    class_tp += 1
                    matched_by_image[image_id][best_index] = True
                else:
                    class_fp += 1
            total_true_positives += class_tp
            total_false_positives += class_fp

    precision = total_true_positives / max(total_true_positives + total_false_positives, 1)
    recall = total_true_positives / max(total_ground_truths, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    mean_ap_per_threshold = [
        float(np.mean(values)) if values else 0.0 for values in all_class_aps
    ]
    return {
        "map": float(np.mean(mean_ap_per_threshold)),
        "map_by_iou": {
            str(threshold): value
            for threshold, value in zip(iou_thresholds, mean_ap_per_threshold)
        },
        "map50": class_metric_mean(class_metrics, "ap50"),
        "map75": class_metric_mean(class_metrics, "ap75"),
        "score_threshold": score_threshold,
        "iou_threshold_for_counts": threshold_for_counts,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "ground_truths": total_ground_truths,
        "true_positives": total_true_positives,
        "false_positives": total_false_positives,
        "classes": class_metrics,
    }


def class_metric_mean(class_metrics: dict[str, Any], key: str) -> float | None:
    values = [
        float(metrics[key])
        for metrics in class_metrics.values()
        if metrics["ground_truths"] and metrics[key] is not None
    ]
    return float(np.mean(values)) if values else None


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
        outputs = model([image.to(device) for image in images])
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
