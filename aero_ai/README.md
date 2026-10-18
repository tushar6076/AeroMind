# AeroMind AI workspaces

`aero_ai/` contains two independent Python projects for model research and
artifact generation:

| Workspace | Purpose | Guide |
| --- | --- | --- |
| `autonomy/` | Telemetry/safety model training, evaluation, and edge export | [`autonomy/README.md`](autonomy/README.md) |
| `vision/` | Aerial-image dataset validation, object-detection training, evaluation, prediction, and ONNX export | [`vision/README.md`](vision/README.md) |

Each workspace has its own `pyproject.toml`, dependencies, configs, source
package, and tests. Install and run them independently; do not install both
projects into one environment unless you deliberately manage their dependency
versions.

These are **training/export workspaces**, not services used at runtime. Model
artifacts are not automatically built into Aero Cloud or loaded by the Flutter
app. Aero Cloud's current AI inventory endpoint returns explicitly marked demo
metadata and does not run inference.

Keep private datasets, credentials, checkpoints, and generated model files out
of Git. Follow each workspace's dataset and validation instructions before
using any model output in an operational workflow.
