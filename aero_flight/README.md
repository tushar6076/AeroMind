# AeroMind Flight Controller

The flight controller is a DYS FC722 running **Betaflight**. Betaflight owns
the real-time flight loop, sensor drivers, stabilization, motor mixing, ESC
output, arming, and failsafe behavior. AeroMind does not maintain a parallel
FC722 firmware implementation here.

This directory records the selected board and defines where future
Betaflight configuration and companion-computer integration artifacts belong:

- [`config/boards/dys_fc722/`](config/boards/dys_fc722/) — hardware profile and
  board-specific verification notes.
- [`integration/`](integration/) — companion-computer/Betaflight interface
  contracts and verified connection details.

Do not assign UARTs, sensor buses, motor outputs, Betaflight target identifiers,
or arming values from the product summary alone. Confirm them against the
specific board revision, wiring harness, receiver, and Betaflight target before
flight testing.

Bluejay is ESC firmware, not flight-controller firmware. Its compatibility,
bidirectional DSHOT, and RPM filtering depend on the separate ESC hardware and
the selected Betaflight/ESC configuration.
