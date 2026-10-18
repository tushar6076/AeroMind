# Aero Vision model workspace

This is an independent Python project for validating aerial-image datasets,
training/evaluating object detectors, running single-image prediction, and
training hierarchical image-classification missions. Detection exports remain
ONNX artifacts. Mission training exports TorchScript `.pth` models and
metadata directly to the Aero Cloud model registry; Aero Cloud catalog
inference is performed by Aero Cloud when the exported trusted TorchScript
weights are installed in the model registry.

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

## Hierarchical mission training

The one-command mission trainer creates the root category router and every
configured model stage, then writes the trained TorchScript artifacts and
metadata into `aero_cloud/models/` by default:

```sh
vision-missions
```

Change the paths and training parameters in
[`configs/missions.yaml`](configs/missions.yaml), or pass an alternate config:

```sh
vision-missions --config path/to/missions.yaml
```

The configured dataset layout is:

```text
data/missions/
├── router/
│   ├── train/<mission-label>/*.jpg
│   └── val/<mission-label>/*.jpg
├── human/
│   ├── person_attributes/
│   │   ├── train/<label>/*.jpg
│   │   └── val/<label>/*.jpg
│   └── clothing/
│       ├── train/<label>/*.jpg
│       └── val/<label>/*.jpg
└── vehicle/
    ├── vehicle_type/
    │   ├── train/<label>/*.jpg
    │   └── val/<label>/*.jpg
    └── vehicle_details/
        ├── train/<label>/*.jpg
        └── val/<label>/*.jpg
```

Each configured train and validation directory must contain one subdirectory
for every label declared in the YAML. Stage directories hold the examples
appropriate to that classifier (for example, person crops for person
attributes and clothing crops for clothing). Keep validation examples separate
from training data. Stage `when` conditions define the inference hierarchy;
they do not filter or relabel the supplied datasets during training.

The trainer uses a small image classifier implemented in this workspace,
resizes images to the configured square input size, converts RGB pixels to
float values in `[0, 1]`, and saves TorchScript files with `.pth` suffixes.
This matches the input and ordered-label contract in
[`../../aero_cloud/models/README.md`](../../aero_cloud/models/README.md).
Validation accuracy is reported for each router/stage model. Model quality,
dataset quality, calibration, and suitability for operational use still
require independent evaluation.

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
predictions. Mission metadata discovery is wired into Aero Cloud, but no live
inference endpoint is implemented yet.
