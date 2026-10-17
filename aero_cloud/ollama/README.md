# ResQVision Tactical Reasoning (Ollama Subsystem)

This folder contains container configuration for the Level 3 tactical reasoning engine.

## Model Lifecycle
- Built on `llama3.2:3b` for fast inference on low-resource companion setups or dedicated cloud nodes.
- Customizes system instructions via `Modelfile` to evaluate aerial search grids and output valid JSON.
- `entrypoint.sh` automatically checks for and builds `resq-tactical:latest` on container startup.