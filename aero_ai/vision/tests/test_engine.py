import numpy as np
from aero_vision_ai.engine.evaluate import evaluate_predictions


def test_evaluate_predictions_metrics():
    predictions = [
        {
            "image_id": 1,
            "boxes": np.array([[50.0, 50.0, 90.0, 90.0]]),
            "labels": np.array([1]),
            "scores": np.array([0.95]),
        }
    ]
    targets = [
        {
            "image_id": 1,
            "boxes": np.array([[50.0, 50.0, 90.0, 90.0]]),
            "labels": np.array([1]),
        }
    ]
    metrics = evaluate_predictions(predictions, targets, ("person",), iou_thresholds=(0.5,))
    assert metrics["map"] == 1.0