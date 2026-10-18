# Autonomy boundary

Reserved for future, safety-gated autonomy decisions. An autonomy component
may propose a bounded high-level action, but must not bypass the verified
flight-session lifecycle, control timeouts, or Betaflight failsafes.

The `aero_ai/autonomy/` workspace contains a separate model-training/export
pipeline. No trained autonomy model is currently wired into Aero Cloud or
flight hardware.
