import numpy as np

from aero_ai.engine.evaluate import evaluate_predictions


def test_perfect_detection_has_unit_ap_precision_recall() -> None:
    predictions = [
        {
            "boxes": np.array([[1, 1, 8, 8]], dtype=float),
            "labels": np.array([1]),
            "scores": np.array([0.95]),
        }
    ]
    targets = [
        {
            "image_id": 7,
            "boxes": np.array([[1, 1, 8, 8]], dtype=float),
            "labels": np.array([1]),
        }
    ]

    metrics = evaluate_predictions(
        predictions, targets, ("person",), (0.5, 0.75), score_threshold=0.25
    )

    assert metrics["map"] == 1.0
    assert metrics["map50"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0


def test_duplicate_detection_is_false_positive() -> None:
    predictions = [
        {
            "boxes": np.array([[1, 1, 8, 8], [1, 1, 8, 8]], dtype=float),
            "labels": np.array([1, 1]),
            "scores": np.array([0.95, 0.8]),
        }
    ]
    targets = [
        {
            "image_id": 2,
            "boxes": np.array([[1, 1, 8, 8]], dtype=float),
            "labels": np.array([1]),
        }
    ]

    metrics = evaluate_predictions(predictions, targets, ("person",), (0.5,))

    assert metrics["true_positives"] == 1
    assert metrics["false_positives"] == 1
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 1.0
