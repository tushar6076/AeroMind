import pytest
from aero_autonomy_ai.config import load_config


def test_load_autonomy_config_success(tmp_path):
    cfg_file = tmp_path / "flight_safety.yaml"
    cfg_file.write_text(
        """
data:
  raw_dir: data/raw
  processed_dir: data/processed
  features: [roll, pitch, yaw_rate, accel_x, accel_y, accel_z]
  window_size: 16
  stride: 4
  val_split: 0.2

model:
  architecture: safety_mlp
  input_dim: 6
  hidden_dims: [32, 16]
  num_classes: 3
  classes: [nominal, motor_fault, battery_critical]
  dropout: 0.05

training:
  output_dir: checkpoints
  epochs: 5
  batch_size: 16
  learning_rate: 0.001
  weight_decay: 0.0001
  seed: 42

export:
  target_format: tflite_int8
  c_array_name: g_safety_model_data
  quantize_calibration_samples: 100
""",
        encoding="utf-8",
    )

    config = load_config(cfg_file)
    assert config.model.architecture == "safety_mlp"
    assert config.model.input_dim == 6
    assert len(config.model.classes) == 3
    assert config.data.window_size == 16
    assert config.export.c_array_name == "g_safety_model_data"


def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("non_existent_config.yaml")