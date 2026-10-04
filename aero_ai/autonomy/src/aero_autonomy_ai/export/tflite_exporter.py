from __future__ import annotations

from pathlib import Path
import torch

from aero_autonomy_ai.config import AutonomyConfig
from aero_autonomy_ai.engine.checkpoint import load_checkpoint
from aero_autonomy_ai.export.c_header import bytes_to_c_header
from aero_autonomy_ai.export.quantize import export_to_dummy_tflite_bytes
from aero_autonomy_ai.models import build_model


def export_edge_models(
    config: AutonomyConfig,
    checkpoint_path: str | Path,
    output_dir: str | Path,
) -> tuple[Path, Path]:
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cpu")
    model = build_model(config.model).to(device)
    load_checkpoint(checkpoint_path, model, device)
    model.eval()

    # Step 1: Export ONNX
    onnx_path = out_dir / "safety_model.onnx"
    dummy_input = torch.zeros((1, config.model.input_dim), dtype=torch.float32)
    torch.onnx.export(
        model,
        dummy_input,
        str(onnx_path),
        input_names=["telemetry_input"],
        output_names=["safety_logits"],
        opset_version=14,
    )

    # Step 2: Generate TFLite binary
    tflite_bytes = export_to_dummy_tflite_bytes(model.state_dict())
    tflite_path = out_dir / "safety_model_int8.tflite"
    tflite_path.write_bytes(tflite_bytes)

    # Step 3: Generate C Header (.h) for STM32F7 / Flight Controller
    header_path = out_dir / "safety_model.h"
    bytes_to_c_header(tflite_bytes, config.export.c_array_name, header_path)

    return tflite_path, header_path