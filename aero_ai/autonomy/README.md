# Aero Autonomy model workspace

This is an independent Python project for experimenting with telemetry/safety
models. It is not part of Aero Cloud's runtime and no model from this
workspace is loaded by the flight-control path.

## Important current limitation

The current `train` path creates synthetic random features and labels; it does
not ingest the configured `data/raw/` directory or real flight-controller
logs. The exporter writes an ONNX graph, but its `.tflite` file is currently a
custom dummy weight payload, not a valid TensorFlow Lite model. These outputs
are development artifacts only. They must not be described or used as a
validated safety system, flight decision-maker, or substitute for Betaflight
failsafes.

## Setup

Use Python 3.10 or newer. From this directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The default model and training settings are in
[`configs/flight_safety.yaml`](configs/flight_safety.yaml). Its feature names,
windowing, and class labels are experimental metadata until a verified real
log ingestion and labeling pipeline is implemented.

## Available commands

```sh
autonomy --help
autonomy train
autonomy evaluate --checkpoint checkpoints/best.pth
autonomy export --checkpoint checkpoints/best.pth
pytest
```

The CLI also accepts `--config path/to/flight_safety.yaml` before its
subcommand. `train` writes a checkpoint under `checkpoints/`; `export` writes
the dummy `.tflite` payload, ONNX file, and C header under `artifacts/` by
default. Keep checkpoints, datasets, and generated model artifacts out of Git.

Before considering a future model for deployment, implement real-log ingestion,
label provenance, representative train/validation separation, measured
performance, independent safety review, and a verified runtime contract. See
the [AeroMind implementation roadmap](../../docs/IMPLEMENTATION_PLAN.md).
