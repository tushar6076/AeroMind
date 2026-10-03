from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import torch
from torch.utils.data import DataLoader

from aero_ai.config import load_config
from aero_ai.data import CocoDetectionDataset, collate_detections, validate_coco_dataset
from aero_ai.deployment import export_onnx
from aero_ai.engine.evaluate import evaluate_model
from aero_ai.engine.train import build_loaders, train
from aero_ai.inference import load_model, predict_image
from aero_ai.models import build_detector
from aero_ai.utils.checkpoint import load_checkpoint

DEFAULT_CONFIG = Path(__file__).resolve().parent / "configs" / "detection.yaml"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resq-ai",
        description="Train, evaluate, and export ResQVision aerial object detectors.",
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to detection YAML config.")
    commands = parser.add_subparsers(dest="command", required=True)
    validate_parser = commands.add_parser("validate", help="Validate train and validation COCO datasets.")
    train_parser = commands.add_parser("train", help="Train Faster R-CNN and save best.pt / last.pt.")

    evaluate_parser = commands.add_parser("evaluate", help="Evaluate a trained checkpoint.")
    evaluate_parser.add_argument("--checkpoint", help="Checkpoint path; defaults to artifacts/best.pt.")
    evaluate_parser.add_argument("--output", help="Optional JSON output path.")

    export_parser = commands.add_parser("export", help="Export a trained detector to ONNX.")
    export_parser.add_argument("--checkpoint", help="Checkpoint path; defaults to artifacts/best.pt.")
    export_parser.add_argument("--output", help="ONNX output path; defaults to artifacts/resq_detector.onnx.")

    predict_parser = commands.add_parser("predict", help="Run detection on one aerial image.")
    predict_parser.add_argument("--image", required=True, help="Input image path.")
    predict_parser.add_argument("--checkpoint", help="Checkpoint path; defaults to artifacts/best.pt.")
    predict_parser.add_argument("--threshold", type=float, help="Override detection confidence threshold.")
    predict_parser.add_argument("--output", help="Optional JSON output path.")
    for command_parser in (
        validate_parser,
        train_parser,
        evaluate_parser,
        export_parser,
        predict_parser,
    ):
        command_parser.add_argument(
            "--config",
            default=argparse.SUPPRESS,
            help="Path to detection YAML config.",
        )
    return parser


def _default_checkpoint(config) -> Path:
    return config.training.output_dir / "best.pt"


def _write_json(document: dict, output: str | None) -> None:
    rendered = json.dumps(document, indent=2)
    if output:
        output_path = Path(output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {output_path}")
    else:
        print(rendered)


def _validate(config) -> None:
    reports = {
        "train": validate_coco_dataset(
            config.data.train_images, config.data.train_annotations, config.model.classes
        ),
        "validation": validate_coco_dataset(
            config.data.val_images, config.data.val_annotations, config.model.classes
        ),
    }
    for split, report in reports.items():
        print(
            f"{split}: {report['images']} images, {report['annotations']} boxes, "
            f"empty images={report['empty_images']}"
        )
        print("  objects per class: " + ", ".join(
            f"{name}={count}" for name, count in report["classes"].items()
        ))
    if not reports["train"]["annotations"]:
        raise ValueError("Training annotations contain no non-crowd bounding boxes.")
    if not reports["validation"]["annotations"]:
        raise ValueError("Validation annotations contain no non-crowd bounding boxes.")


def _evaluate(config, checkpoint: str | None, output: str | None) -> None:
    selected_device = torch.device(
        "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    )
    model = build_detector(config.model).to(selected_device)
    checkpoint_path = Path(checkpoint) if checkpoint else _default_checkpoint(config)
    load_checkpoint(checkpoint_path, model, config.model.classes, selected_device)
    dataset = CocoDetectionDataset(
        config.data.val_images, config.data.val_annotations, config.model.classes
    )
    loader = DataLoader(
        dataset,
        batch_size=config.training.batch_size,
        shuffle=False,
        num_workers=config.training.num_workers,
        collate_fn=collate_detections,
        pin_memory=selected_device.type == "cuda",
    )
    metrics = evaluate_model(
        model,
        loader,
        selected_device,
        config.model.classes,
        config.evaluation.iou_thresholds,
        config.evaluation.score_threshold,
    )
    metrics["checkpoint"] = str(checkpoint_path.resolve())
    _write_json(metrics, output)


def _predict(config, image: str, checkpoint: str | None, threshold: float | None, output: str | None) -> None:
    checkpoint_path = Path(checkpoint) if checkpoint else _default_checkpoint(config)
    model, device = load_model(config, checkpoint_path)
    result = predict_image(
        model,
        image,
        config.model.classes,
        device,
        config.evaluation.score_threshold if threshold is None else threshold,
    )
    _write_json(result, output)


def main(argv: Sequence[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    config = load_config(args.config)
    if args.command == "validate":
        _validate(config)
    elif args.command == "train":
        train(config)
    elif args.command == "evaluate":
        _evaluate(config, args.checkpoint, args.output)
    elif args.command == "export":
        output = Path(args.output) if args.output else config.training.output_dir / "resq_detector.onnx"
        path = export_onnx(
            config,
            args.checkpoint or _default_checkpoint(config),
            output,
        )
        print(f"Exported ONNX detector: {path}")
    elif args.command == "predict":
        _predict(config, args.image, args.checkpoint, args.threshold, args.output)
    else:
        raise RuntimeError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    main()
