# AeroMind AI workspaces

`aero_ai/` contains two independent Python projects for model research and
artifact generation:

| Workspace | Purpose | Guide |
| --- | --- | --- |
| `autonomy/` | Telemetry/safety model training, evaluation, and edge export | [`autonomy/README.md`](autonomy/README.md) |
| `vision/` | Aerial-image detection workflows plus one-command hierarchical mission training and TorchScript registry export | [`vision/README.md`](vision/README.md) |

Each workspace has its own `pyproject.toml`, dependencies, configs, source
package, and tests. Install and run them independently; do not install both
projects into one environment unless you deliberately manage their dependency
versions.

These are **training/export workspaces**, not services used at runtime. The
`vision-missions` command writes TorchScript files and manifests to
`aero_cloud/models/`; Aero Cloud discovers their metadata and runs hierarchical
inference from the authenticated image endpoint when trusted weights are
available. Detection ONNX exports remain a separate workflow and are not part
of the TorchScript mission registry.

Keep private datasets, credentials, checkpoints, and generated model files out
of Git. Follow each workspace's dataset and validation instructions before
using any model output in an operational workflow.
