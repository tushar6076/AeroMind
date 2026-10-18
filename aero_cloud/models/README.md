# Aero Cloud model registry

This directory is the read-only model registry mounted into Aero Cloud. Keep
trained model weights local; `.pth` files under this directory are ignored by
Git. Do not load model files from untrusted sources.

## Layout

```text
models/
├── README.md
├── router.json
├── router.pth
├── human/
│   ├── metadata.json
│   └── *.pth
└── vehicle/
    ├── metadata.json
    └── *.pth
```

`router.pth` is the root TorchScript classifier. `router.json` declares its
input tensor, output labels, and label-to-mission mapping. Each category
directory with a valid `metadata.json` is discovered as an app mission the
next time the app refreshes its AI loadout. Discovery is independent of the
router weights: a mission can appear in the catalog while reporting that it is
not yet runnable.

Add a category by creating a lowercase `models/<category>/` directory and a
valid `metadata.json` there. The metadata `id` must match the directory name.
Use unique stage IDs and TorchScript `.pth` artifact paths relative to that
category directory. To make the router select the category, its output label
must also be present in `router.json` and map to the category ID, and the
trained `router.pth` must emit that label.

## Inference contract

- Artifacts use TorchScript, saved with a `.pth` extension. A conventional
  PyTorch state dictionary is not a runnable artifact.
- Every model receives one RGB image tensor with shape `[1, 3, height, width]`,
  `float32` values in the declared range. Preprocessing must match the
  corresponding metadata exactly.
- Classifier outputs are ordered class scores matching the declared labels.
- Mission stages are evaluated in listed order. A stage with `when` runs only
  when the named earlier stage emitted one of the listed labels.
- Artifact paths must remain inside the router or mission directory. Absolute
  paths, parent-directory traversal, and links outside the model directory are
  not supported.

The API validates metadata and reports artifact state in the
`GET /api/v1/ai/loadout` catalog. The authenticated `POST /api/v1/ai/infer`
endpoint accepts a JPEG, PNG, or WebP raw request body, runs the router, then
evaluates applicable mission stages in order. Models are loaded lazily on CPU
and cached until their file signature changes. Missing or incompatible weights
produce an explicit unavailable response; no image is persisted.

A status of “Weights present; not yet loaded” means only that the expected
files exist. The status becomes “Loaded and ready” after successful inference
loads those weights. TorchScript artifacts execute code and must be trusted.

## Current categories

- `human/`: example multi-stage person-attribute and clothing classification
  contract. It contains no weights. Attribute results are model predictions,
  not verified identity or ground truth.
- `vehicle/`: example vehicle classification and follow-up-detail contract.
  It contains no weights.

To add weights locally, place each file at the path named in its metadata.
Compose mounts this directory read-only at `/app/models`; local Python runs
use this directory by default. Set `AI_MODELS_DIR` to use a different registry
path. Configure `AI_MAX_IMAGE_BYTES` and `AI_MAX_IMAGE_PIXELS` to change the
inference request limits.
