from __future__ import annotations

import json
from pathlib import Path

import torch

from aero_ai.config import AppConfig
from aero_ai.models import build_detector
from aero_ai.utils.checkpoint import load_checkpoint


class OnnxDetectionWrapper(torch.nn.Module):
    def __init__(self, detector: torch.nn.Module) -> None:
        super().__init__()
        self.detector = detector

    def forward(self, images: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        result = self.detector([images[0]])[0]
        return result["boxes"], result["scores"], result["labels"]


def export_onnx(
    config: AppConfig,
    checkpoint_path: str | Path,
    output_path: str | Path,
    device: torch.device | None = None,
) -> Path:
    selected_device = device or torch.device("cpu")
    detector = build_detector(config.model).to(selected_device)
    load_checkpoint(checkpoint_path, detector, config.model.classes, selected_device)
    detector.eval()
    detector.roi_heads.detections_per_img = config.export.max_detections
    wrapper = OnnxDetectionWrapper(detector).eval()
    dummy_input = torch.zeros(
        (1, 3, config.export.input_size, config.export.input_size),
        dtype=torch.float32,
        device=selected_device,
    )
    target_path = Path(output_path).expanduser().resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        wrapper,
        dummy_input,
        str(target_path),
        input_names=["images"],
        output_names=["boxes", "scores", "labels"],
        dynamic_axes={
            "boxes": {0: "detections"},
            "scores": {0: "detections"},
            "labels": {0: "detections"},
        },
        opset_version=config.export.opset,
        do_constant_folding=True,
    )

    import onnx

    onnx_model = onnx.load(str(target_path))
    onnx.checker.check_model(onnx_model)
    metadata_path = target_path.with_suffix(".json")
    metadata_path.write_text(
        json.dumps(
            {
                "task": "object_detection",
                "architecture": "Faster R-CNN ResNet-50 FPN",
                "input": {
                    "name": "images",
                    "shape": [1, 3, config.export.input_size, config.export.input_size],
                    "layout": "NCHW",
                    "color": "RGB",
                    "range": [0.0, 1.0],
                },
                "outputs": {
                    "boxes": "xyxy pixel coordinates in the original input image",
                    "scores": "confidence score for each detection",
                    "labels": "1-based configured category id",
                },
                "classes": list(config.model.classes),
                "score_threshold": config.evaluation.score_threshold,
                "opset": config.export.opset,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return target_path
