# DYS FC722 board profile

`board.yaml` records the supplied FC722 specifications. It is descriptive
hardware metadata, not a Betaflight target definition or a pin map.

Before creating or applying a Betaflight configuration, verify:

1. The exact MCU marking and Betaflight target for this board revision.
2. The board-revision-specific pinout, UART assignments, I2C labels, and sensor
   bus assignments. The supplied text says `SDA / SLA`; verify the second pad
   marking rather than assuming it is `SCL`.
3. Receiver protocol and wiring, motor numbering/order, and ESC firmware.
4. Whether the ESC actually supports Bluejay, bidirectional DSHOT, and RPM
   filtering; these are not established by the flight-controller MCU.
5. Blackbox flash detection and configured storage before relying on logs.
6. BEC rail limits and peripheral power requirements against the board manual.

Keep verified target names, board revisions, and wiring maps in this directory
only after they have been checked against the physical board and authoritative
manufacturer or Betaflight documentation.
