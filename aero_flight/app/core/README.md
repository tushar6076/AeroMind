# Core boundary

Reserved for a future companion-side lifecycle, configuration validation,
health state, and structured logging. Keep hardware access behind explicit
interfaces; do not open device connections at module import time.

No runtime code is implemented here. The active API application lifecycle is
currently in `aero_cloud/app/main.py`.
