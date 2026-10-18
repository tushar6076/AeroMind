# External sensor interfaces

Reserved for external sensors attached to a companion computer. Sensor data
already measured by the FC should be consumed through a verified telemetry
interface rather than read a second time from guessed pins.

Before adding an interface, document units, sample rate, timestamp source,
staleness behavior, and how missing or invalid samples affect readiness.
