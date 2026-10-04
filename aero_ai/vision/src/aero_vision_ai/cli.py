from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import torch
from torch.utils.data import DataLoader

from aero_vision_ai.config import load_config
from aero_vision_ai.data import CocoDetectionDataset, collate_detections, validate_coco_dataset
from aero_vision_ai.engine import (
    evaluate_model,
    export_onnx,
    load_checkpoint,
    train,
)
from aero_vision_ai.inference import load_model, predict_image
from aero_vision_ai.models import build_detector

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "detection.yaml"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vision",
        description="ResQVision aerial detection command-line suite.",
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to YAML configuration.")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("validate", help="Validate COCO annotations.")
    commands.add_parser("train", help="Train aerial detector.")

    eval_p = commands.add_parser("evaluate", help="Evaluate checkpoint.")
    eval_p.add_argument("--checkpoint", help="Path to checkpoint.")
    eval_p.add_argument("--output", help="Output JSON path.")

    exp_p = commands.add_parser("export", help="Export to ONNX.")
    exp_p.add_argument("--checkpoint", help="Path to checkpoint.")
    exp_p.add_argument("--output", help="Output ONNX path.")

    pred_p = commands.add_parser("predict", help="Predict single image.")
    pred_p.add_argument("--image", required=True, help="Path to input image.")
    pred_p.add_argument("--checkpoint", help="Path to checkpoint.")
    pred_p.add_argument("--threshold", type=float, help="Confidence threshold.")
    pred_p.add_argument("--output", help="Output JSON path.")

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    config = load_config(args.config)

    if args.command == "validate":
        print("[*] Validating train dataset:")
        train_rep = validate_coco_dataset(config.data.train_images, config.data.train_annotations, config.model.classes)
        print(f"  Images: {train_rep['images']}, Boxes: {train_rep['annotations']}, Classes: {train_rep['classes']}")
        print("[*] Validating val dataset:")
        val_rep = validate_coco_dataset(config.data.val_images, config.data.val_annotations, config.model.classes)
        print(f"  Images: {val_rep['images']}, Boxes: {val_rep['annotations']}, Classes: {val_rep['classes']}")

    elif args.command == "train":
        train(config)

    elif args.command == "evaluate":
        dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = build_detector(config.model).to(dev)
        ckpt = Path(args.checkpoint) if args.checkpoint else config.training.output_dir / "best.pt"
        load_checkpoint(ckpt, model, config.model.classes, dev)
        dataset = CocoDetectionDataset(config.data.val_images, config.data.val_annotations, config.model.classes)
        loader = DataLoader(dataset, batch_size=config.training.batch_size, collate_fn=collate_detections)
        metrics = evaluate_model(model, loader, dev, config.model.classes, config.evaluation.iou_thresholds, config.evaluation.score_threshold)
        rendered = json.dumps(metrics, indent=2)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered)

    elif args.command == "export":
        ckpt = Path(args.checkpoint) if args.checkpoint else config.training.output_dir / "best.pt"
        out = Path(args.output) if args.output else config.root / "artifacts" / "aero_detector.onnx"
        export_onnx(config, ckpt, out)
        print(f"[✓] Exported ONNX to {out}")

    elif args.command == "predict":
        ckpt = Path(args.checkpoint) if args.checkpoint else config.training.output_dir / "best.pt"
        model, dev = load_model(config, ckpt)
        res = predict_image(model, args.image, config.model.classes, dev, args.threshold or config.evaluation.score_threshold)
        rendered = json.dumps(res, indent=2)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered)


if __name__ == "__main__":
    main()