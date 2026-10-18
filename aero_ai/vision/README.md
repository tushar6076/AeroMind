# Aero Vision model workspace

This is an independent Python project for validating aerial-image datasets,
training/evaluating object detectors, running single-image prediction, and
exporting ONNX. It is not part of the Aero Cloud container; exported models
must be integrated explicitly before the app can use them.

The default config defines `person`, `vehicle`, and `animal` classes and a
Faster R-CNN ResNet-50 detector. These are model class labels, not a claim that
the model has been trained or validated for an operational use.

## Setup

Use Python 3.10 or newer. From this directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Training may download Torchvision pretrained weights because
`model.pretrained` is enabled in `configs/detection.yaml`. Set it to `false`
for an offline run or if downloading is not appropriate. Install a PyTorch
build appropriate for your compute hardware when GPU acceleration is needed.

## Dataset

The default config expects:

```text
data/raw/
├── images/
│   ├── train/
│   └── val/
└── annotations/
    ├── train.json
    └── val.json
```

Annotations use COCO JSON with `images`, `categories`, and `annotations`
arrays. Category names must match `model.classes` in
[`configs/detection.yaml`](configs/detection.yaml). Bounding boxes use
`[x, y, width, height]` pixel coordinates. Keep train and validation images
separate, use only data you have permission to use, and do not commit private
imagery or generated checkpoints.

Edit the YAML paths to use another dataset layout. Paths are resolved relative
to the directory containing the YAML config.

## Workflow

Run from this directory after installing dependencies and preparing the
dataset:

```sh
vision validate
vision train
vision evaluate --checkpoint checkpoints/best.pt
vision predict --image data/raw/images/val/frame_0001.jpg \
  --checkpoint checkpoints/best.pt
vision export --checkpoint checkpoints/best.pt
pytest
```

Pass a different config with `vision --config path/to/detection.yaml validate`
(the global `--config` option goes before the command). Training writes
`checkpoints/best.pt` and `checkpoints/last.pt`; ONNX export writes
`artifacts/aero_detector.onnx` plus a metadata JSON sidecar by default.

Inspect evaluation results on representative validation imagery before using
predictions. There is currently no live inference endpoint, model registry,
or automatic model deployment in Aero Cloud.
