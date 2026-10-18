# Companion-side flight scaffold

This tree reserves boundaries for possible AeroMind-side hardware adapters;
it does not contain executable firmware or a second flight-control loop.

Aero Cloud currently implements the API-facing flight service and CRSF bridge.
Before adding code here, decide whether the capability belongs in Aero Cloud
or in a separate companion process. Record the protocol, authority, timeout,
and failure behavior in `../integration/` first. Betaflight remains the
real-time stabilization, motor-output, and failsafe authority.
