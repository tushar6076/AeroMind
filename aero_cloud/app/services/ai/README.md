# AI catalog service

The AI catalog is filesystem-discovered from `AI_MODELS_DIR`. Its expected
structure and TorchScript metadata format are documented in
[`../../../models/README.md`](../../../models/README.md).

`AIService.inventory()` rescans `router.json` and each immediate category
directory's `metadata.json` for every loadout request. It validates metadata,
checks that declared artifacts stay within their model directory, and reports
invalid metadata or missing files in the API response. This makes a newly
added valid mission visible to the ground-station app after refreshing its
catalog without changing Flutter code or restarting Aero Cloud.

The authenticated `POST /api/v1/ai/infer` endpoint accepts JPEG, PNG, or WebP
image bytes. It preprocesses each image to the dimensions and value range in
the router/mission metadata, runs the router, then evaluates stages in order
while honoring their `when` conditions. Each TorchScript model must return a
`[1, number_of_labels]` tensor of class logits in the label order in metadata.
The response contains the router choice and confidence, plus a prediction or
an explicit skipped status for each mission stage.

Artifacts load lazily onto CPU and are cached by path and file signature.
Missing weights, invalid TorchScript files, and invalid model outputs result
in explicit service-unavailable responses. Uploaded images require the
configured API access token, have a bounded request size and decoded pixel
count, and are not persisted. Only load trusted model artifacts; inference
executes their TorchScript code.
