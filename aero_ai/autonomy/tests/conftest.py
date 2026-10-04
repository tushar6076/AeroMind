import numpy as np
import pytest
from aero_autonomy_ai.config import AutonomyConfig, DataConfig, ExportConfig, ModelConfig, TrainingConfig


@pytest.fixture
def dummy_config(tmp_path):
    return AutonomyConfig(
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
            hidden_dims=(16, 8),
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
            c_array_name="g_test_model",
            quantize_calibration_samples=50,
        ),
    )