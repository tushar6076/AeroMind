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
