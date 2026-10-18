# Companion-computer integration

This area is for verified interfaces between Aero Cloud/the edge computer and
Betaflight on the FC722. It does not contain a second flight-control stack.

Record an interface here only after its physical and protocol details have
been verified:

- Receiver/CRSF wiring and companion-computer serial interface.
- Betaflight MSP telemetry or configuration transport, if used.
- UART assignment and serial-port function for the actual FC722 board revision.
- Startup, link-loss, disarm, and recovery behavior shared with Aero Cloud.

The product summary provides six UARTs but no pinout, UART numbering, or serial
function mapping. Those values remain intentionally unspecified until the
board-specific wiring diagram is available.

## Verification record to complete before implementation

For each installed aircraft revision, record:

- FC722 board revision, MCU marking, and Betaflight target/version.
- Source and revision of the authoritative wiring/pinout documentation.
- Receiver model, protocol, physical UART, Betaflight serial-port function,
  and baud/configuration.
- Channel order/direction, verified arm channel, and disarm value.
- FC failsafe configuration and observed behavior for receiver/link loss.
- Companion OS/device node, permissions, and serial adapter used by Aero Cloud.
- Test date, test operator, propeller-removed bench result, and any outstanding
  hazards.

Leave unknown values explicitly unknown; do not copy a guessed mapping into
Compose, `.env`, or the board profile. The top-level
[`docs/IMPLEMENTATION_PLAN.md`](../../docs/IMPLEMENTATION_PLAN.md) defines the
hardware verification gate.
