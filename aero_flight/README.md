# Aero Flight

This directory is the hardware and flight-controller integration workspace.
Its confirmed board profile is a **DYS FC722 running Betaflight**. Betaflight
owns the real-time stabilization loop, sensors attached to the FC, motor
mixing, ESC output, and FC failsafes. AeroMind does not implement a replacement
flight-controller firmware here.

The current `app/` tree is a **documentation-only scaffold** for future
companion-side adapters and verified integration boundaries. It contains no
runnable flight code. Aero Cloud currently owns the app-facing flight API and
CRSF bridge. Do not duplicate those services or move control authority into a
new process without an explicit architecture decision and safety review.

## Structure

| Path | Intended responsibility | Status |
| --- | --- | --- |
| [`app/core/`](app/core/README.md) | Future edge-adapter lifecycle, typed config, and health contracts | Scaffold only |
| [`app/communication/`](app/communication/README.md) | Verified CRSF/MSP transport contracts and protocol boundaries | Scaffold only |
| [`app/drivers/`](app/drivers/README.md) | Board-specific peripheral adapters, if Aero Cloud does not own them | Scaffold only |
| [`app/sensors/`](app/sensors/README.md) | External sensor interfaces not already owned by Betaflight | Scaffold only |
| [`app/flight/`](app/flight/README.md) | High-level mode/session coordination contract; no stabilization or motor loop | Scaffold only |
| [`app/autonomous/`](app/autonomous/README.md) | Future safety-gated autonomy decisions and command proposals | Scaffold only |
| [`app/utils/`](app/utils/README.md) | Small shared helpers after a demonstrated need | Scaffold only |
| [`config/boards/dys_fc722/`](config/boards/dys_fc722/README.md) | Supplied hardware metadata and board-revision verification notes | Descriptive profile; not a pin map |
| [`integration/`](integration/README.md) | Verified companion/FC wiring, protocol, and failsafe contracts | Documentation only |

## Implementation order and safety boundary

1. Confirm the exact FC722 hardware revision and Betaflight target on the
   physical board.
2. Record the authoritative wiring diagram, receiver/CRSF wiring, UART map,
   channel map, and configured FC failsafes in `integration/`.
3. Bench-test telemetry and disarm behavior with propellers removed.
4. Only then implement a narrowly scoped adapter or integration test, with
   explicit ownership and timeout behavior agreed with Aero Cloud.
5. Keep any future autonomy output as a bounded, validated high-level
   proposal. Betaflight continues to enforce stabilization and FC failsafes.

Do not infer UART numbers, serial functions, motor order, sensor bus mappings,
arming channel, target identifier, or ESC capability from the board name or
product summary. The board profile still contains supplier-provided values
that require verification.

Bluejay is ESC firmware, not flight-controller firmware. Confirm ESC
compatibility and bidirectional DSHOT/RPM filtering against the actual ESC and
Betaflight configuration.
