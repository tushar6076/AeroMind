# High-level flight coordination

Reserved for a future companion-side contract for high-level modes and
validated command proposals. It must not implement stabilization, motor
mixing, direct ESC output, or a parallel arming/failsafe authority.

Aero Cloud currently owns API-level flight sessions, readiness checks, and
the CRSF control bridge. Betaflight remains authoritative for the real-time
flight loop and FC failsafe behavior.
