from pathlib import Path
import torch

from aero_autonomy_ai.config import AutonomyConfig, DataConfig, ExportConfig, ModelConfig, TrainingConfig
from aero_autonomy_ai.engine.checkpoint import save_checkpoint
from aero_autonomy_ai.export.c_header import bytes_to_c_header
from aero_autonomy_ai.export.tflite_exporter import export_edge_models
from aero_autonomy_ai.models.safety_mlp import FlightSafetyMLP


def test_bytes_to_c_header(tmp_path):
    dummy_bytes = b"\x01\x02\x03\x04\x0a\x0b\x0c"
    out_h = tmp_path / "model.h"
    res = bytes_to_c_header(dummy_bytes, "g_test_model", out_h)

    assert res.is_file()
    content = out_h.read_text(encoding="utf-8")
    assert "const unsigned int g_test_model_len = 7;" in content
    assert "0x01, 0x02, 0x03, 0x04" in content
    assert "#ifndef RESQ_SAFETY_MODEL_H" in content


def test_export_edge_models_full(tmp_path):
    cfg = AutonomyConfig(
        root=tmp_path,
        data=DataConfig(
            raw_dir=tmp_path / "raw",
            processed_dir=tmp_path / "proc",
            features=("f1", "f2", "f3"),
            window_size=8,
            stride=2,
            val_split=0.2,
        ),
        model=ModelConfig(
            architecture="safety_mlp",
            input_dim=3,
            hidden_dims=(8,),
            num_classes=2,
            classes=("nominal", "fault"),
            dropout=0.0,
        ),
        training=TrainingConfig(
            output_dir=tmp_path / "checkpoints",
            epochs=1,
            batch_size=8,
            learning_rate=0.01,
            weight_decay=0.0,
            seed=42,
        ),
        export=ExportConfig(
            target_format="tflite_int8",
            c_array_name="g_safety_model",
            quantize_calibration_samples=20,
        ),
    )

    # Prepare a checkpoint
    model = FlightSafetyMLP(cfg.model)
    opt = torch.optim.Adam(model.parameters())
    ckpt_path = tmp_path / "best.pth"
    save_checkpoint(ckpt_path, model, opt, 1, 0.9, cfg.model.classes)

    out_dir = tmp_path / "artifacts"
    tflite_path, header_path = export_edge_models(cfg, ckpt_path, out_dir)

    assert tflite_path.is_file()
    assert header_path.is_file()
    assert (out_dir / "safety_model.onnx").is_file()