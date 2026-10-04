from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

import torch
from aero_autonomy_ai.config import load_config
from aero_autonomy_ai.engine import evaluate_model, load_checkpoint, train
from aero_autonomy_ai.engine.train import create_synthetic_data
from aero_autonomy_ai.export import export_edge_models
from aero_autonomy_ai.models import build_model

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "flight_safety.yaml"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autonomy",
        description="ResQVision Level 1 flight safety and edge telemetry AI suite.",
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to YAML configuration.")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("train", help="Train flight safety decision model.")

    eval_p = commands.add_parser("evaluate", help="Evaluate model against telemetry benchmarks.")
    eval_p.add_argument("--checkpoint", help="Path to checkpoint.")
    eval_p.add_argument("--output", help="Output JSON path.")

    exp_p = commands.add_parser("export", help="Quantize & export to TFLite and C-header.")
    exp_p.add_argument("--checkpoint", help="Path to checkpoint.")
    exp_p.add_argument("--output", help="Artifacts directory.")

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    config = load_config(args.config)

    if args.command == "train":
        train(config)

    elif args.command == "evaluate":
        dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = build_model(config.model).to(dev)
        ckpt = Path(args.checkpoint) if args.checkpoint else config.training.output_dir / "best.pth"
        load_checkpoint(ckpt, model, dev)
        _, val_loader = create_synthetic_data(config)
        metrics = evaluate_model(model, val_loader, dev, config.model.classes)
        rendered = json.dumps(metrics, indent=2)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered)

    elif args.command == "export":
        ckpt = Path(args.checkpoint) if args.checkpoint else config.training.output_dir / "best.pth"
        out_dir = Path(args.output) if args.output else config.root / "artifacts"
        tf_path, h_path = export_edge_models(config, ckpt, out_dir)
        print(f"[✓] Exported TFLite int8 -> {tf_path}")
        print(f"[✓] Exported C Header    -> {h_path}")


if __name__ == "__main__":
    main()